const Stripe = require('stripe');

// Vercel parses the body by default, which breaks Stripe's signature check —
// it needs the exact raw bytes that were signed, not a re-serialized object.
module.exports.config = { api: { bodyParser: false } };

function readRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

// Shared by both fulfillment paths (redirect-based Checkout Sessions and the
// embedded Payment Element flow) — Admin-Backend's claim endpoint only ever
// wants an opaque unique id plus the purchase details; it never cares
// whether that id came from a Checkout Session (cs_...) or a PaymentIntent
// created directly (pi_...), so this same call works for either.
async function submitCreditsClaim({ idempotencyId, email, credits, amountCharged, currency, stripePaymentIntentId }) {
  if (!email) {
    console.error('SideKix [website credits claim] no email for', idempotencyId);
    return { ok: true };
  }
  if (!Number.isInteger(credits) || credits <= 0) {
    console.error('SideKix [website credits claim] missing/invalid credits metadata for', idempotencyId);
    return { ok: true };
  }

  const claimRes = await fetch(
    'https://api.sidekixhq.com/internal/website-credits/claims',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-internal-key': process.env.WEBSITE_INTERNAL_KEY || '',
        // Admin-Backend's global DeviceIdGuard requires this on every route
        // not explicitly exempted (admin/otp/rbac/uploads/payments) — found
        // by actually running this call locally; without it every request
        // 400s before WebsiteInternalGuard ever runs.
        'x-device-agent': 'web',
      },
      body: JSON.stringify({
        sessionId: idempotencyId,
        email,
        credits,
        amountCharged,
        currency,
        stripePaymentIntentId,
      }),
    },
  );
  if (!claimRes.ok) {
    const body = await claimRes.text().catch(() => '');
    throw new Error(`Admin-Backend responded ${claimRes.status}: ${body}`);
  }
  return { ok: true };
}

// The failed-payment counterpart to submitCreditsClaim above — previously a
// declined card or an abandoned checkout left no record anywhere at all.
// Unlike a successful claim, there's nothing to grant here, so a missing
// email just means "nothing useful to log", not an error — an entirely
// abandoned session that never got that far genuinely has no destination
// for this record.
async function submitCheckoutFailure({ email, credits, packs, amountAttempted, currency, stripeCheckoutSessionId, stripePaymentIntentId, failureReason }) {
  if (!email) {
    console.log('SideKix [website checkout failure] no email captured, nothing to log for', stripePaymentIntentId || stripeCheckoutSessionId);
    return;
  }
  const failureRes = await fetch(
    'https://api.sidekixhq.com/internal/website-credits/failures',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-internal-key': process.env.WEBSITE_INTERNAL_KEY || '',
        'x-device-agent': 'web',
      },
      body: JSON.stringify({
        email,
        credits: Number.isInteger(credits) && credits > 0 ? credits : 1,
        packs,
        amountAttempted,
        currency,
        stripeCheckoutSessionId,
        stripePaymentIntentId,
        failureReason,
      }),
    },
  );
  if (!failureRes.ok) {
    const body = await failureRes.text().catch(() => '');
    throw new Error(`Admin-Backend responded ${failureRes.status}: ${body}`);
  }
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).end();
    return;
  }

  const rawBody = await readRawBody(req);
  const signature = req.headers['stripe-signature'];

  // Live and test webhooks are both registered against this one URL (there's
  // no separate staging domain for this site), so a single incoming request
  // could be signed with either secret. Try each configured one in turn
  // rather than picking a single env var, so a test-mode Checkout session
  // run directly against the deployed site verifies correctly too.
  const candidateSecrets = [
    process.env.STRIPE_WEBHOOK_SECRET,
    process.env.STRIPE_WEBHOOK_SECRET_TEST,
  ].filter(Boolean);

  let event;
  for (const secret of candidateSecrets) {
    try {
      event = Stripe.webhooks.constructEvent(rawBody, signature, secret);
      break;
    } catch (err) {
      continue;
    }
  }

  if (!event) {
    console.error('Webhook signature verification failed against all configured secrets.');
    res.status(400).send('Webhook Error: signature verification failed');
    return;
  }

  // Both cover fulfillment: `completed` fires immediately for card payments,
  // `async_payment_succeeded` fires later for delayed methods (e.g. bank
  // debits) that finish after the redirect — checking `payment_status` on
  // both handles either without double-counting a session that was
  // `completed` but still `unpaid` pending an async method.
  if (
    (event.type === 'checkout.session.completed' || event.type === 'checkout.session.async_payment_succeeded') &&
    event.data.object.payment_status === 'paid'
  ) {
    const session = event.data.object;
    // No account system on this site to grant anything into yet — Stripe's
    // dashboard + its automatic receipt email are the system of record for
    // now. This log is what ties a Vercel deploy's function logs back to a
    // specific pre-order if support ever needs to trace one down.
    console.log('SideKix website pre-order paid:', {
      sessionId: session.id,
      customerEmail: session.customer_details?.email,
      type: session.metadata?.type,
      plan: session.metadata?.plan,
      packs: session.metadata?.packs,
      amountTotal: session.amount_total,
    });

    // Credits (not membership pre-orders) get a claim link: record the
    // purchase in Admin-Backend and email the buyer a link to log into
    // their real account and have the credits added. Non-2xx here makes
    // Stripe redeliver this whole webhook later — safe, since the
    // internal endpoint is idempotent on sessionId (won't double-create
    // the claim or re-send the email on a retry that already succeeded).
    if (session.metadata?.type === 'credits') {
      // Read the exact amount create-checkout-session.js stored — never
      // recompute packs * CREDIT_PACK_SIZE here (that constant used to be
      // duplicated in both files with nothing keeping them in sync). A
      // session with no credits metadata (e.g. one created manually in the
      // Stripe Dashboard for testing) fails loudly instead of silently
      // granting a guessed amount.
      try {
        await submitCreditsClaim({
          idempotencyId: session.id,
          email: session.customer_details?.email,
          credits: parseInt(session.metadata?.credits, 10),
          // amount_total is in the smallest currency unit (cents for usd) —
          // convert to major units for CreditPurchaseIntent, which stores
          // dollars like the rest of that table.
          amountCharged: typeof session.amount_total === 'number' ? session.amount_total / 100 : undefined,
          currency: session.currency,
          stripePaymentIntentId:
            typeof session.payment_intent === 'string' ? session.payment_intent : session.payment_intent?.id,
        });
      } catch (err) {
        console.error('SideKix [website credits claim] failed:', err);
        res.status(502).json({ error: 'Could not record credits claim, will retry' });
        return;
      }
    }
  }

  // The embedded Payment Element flow (create-payment-intent.js) never
  // creates a Checkout Session — the PaymentIntent itself carries the same
  // metadata shape, and its own id is a perfectly good unique idempotency
  // key for the claim (Admin-Backend's endpoint treats it as an opaque
  // string either way — see submitCreditsClaim above).
  if (event.type === 'payment_intent.succeeded' && event.data.object.metadata?.type === 'credits') {
    const intent = event.data.object;
    console.log('SideKix website embedded credits purchase paid:', {
      paymentIntentId: intent.id,
      email: intent.metadata?.email,
      packs: intent.metadata?.packs,
      amountReceived: intent.amount_received,
    });
    try {
      await submitCreditsClaim({
        idempotencyId: intent.id,
        email: intent.metadata?.email,
        credits: parseInt(intent.metadata?.credits, 10),
        amountCharged: typeof intent.amount_received === 'number' ? intent.amount_received / 100 : undefined,
        currency: intent.currency,
        stripePaymentIntentId: intent.id,
      });
    } catch (err) {
      console.error('SideKix [website credits claim] failed:', err);
      res.status(502).json({ error: 'Could not record credits claim, will retry' });
      return;
    }
  }

  // Failure/cancellation counterparts to the two success paths above — a
  // declined card, an abandoned session, or an explicitly cancelled
  // PaymentIntent previously left no database record at all.
  if (
    (event.type === 'payment_intent.payment_failed' || event.type === 'payment_intent.canceled') &&
    event.data.object.metadata?.type === 'credits'
  ) {
    const intent = event.data.object;
    try {
      await submitCheckoutFailure({
        email: intent.metadata?.email,
        credits: parseInt(intent.metadata?.credits, 10),
        packs: parseInt(intent.metadata?.packs, 10) || undefined,
        // intent.amount (not amount_received) — nothing was actually
        // received, this is what was attempted.
        amountAttempted: typeof intent.amount === 'number' ? intent.amount / 100 : undefined,
        currency: intent.currency,
        stripePaymentIntentId: intent.id,
        failureReason: intent.last_payment_error?.message || (event.type === 'payment_intent.canceled' ? 'Payment cancelled' : 'Payment failed'),
      });
    } catch (err) {
      console.error('SideKix [website checkout failure] failed to log:', err);
      res.status(502).json({ error: 'Could not record checkout failure, will retry' });
      return;
    }
  }

  if (
    (event.type === 'checkout.session.expired' || event.type === 'checkout.session.async_payment_failed') &&
    event.data.object.metadata?.type === 'credits'
  ) {
    const session = event.data.object;
    try {
      await submitCheckoutFailure({
        email: session.customer_details?.email,
        credits: parseInt(session.metadata?.credits, 10),
        packs: parseInt(session.metadata?.packs, 10) || undefined,
        amountAttempted: typeof session.amount_total === 'number' ? session.amount_total / 100 : undefined,
        currency: session.currency,
        stripeCheckoutSessionId: session.id,
        stripePaymentIntentId:
          typeof session.payment_intent === 'string' ? session.payment_intent : session.payment_intent?.id,
        failureReason: event.type === 'checkout.session.expired' ? 'Checkout session expired (abandoned)' : 'Async payment failed',
      });
    } catch (err) {
      console.error('SideKix [website checkout failure] failed to log:', err);
      res.status(502).json({ error: 'Could not record checkout failure, will retry' });
      return;
    }
  }

  res.status(200).json({ received: true });
};
