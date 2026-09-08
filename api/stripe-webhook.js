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
      const email = session.customer_details?.email;
      // Read the exact amount create-checkout-session.js stored — never
      // recompute packs * CREDIT_PACK_SIZE here (that constant used to be
      // duplicated in both files with nothing keeping them in sync). A
      // session with no credits metadata (e.g. one created manually in the
      // Stripe Dashboard for testing) fails loudly instead of silently
      // granting a guessed amount.
      const credits = parseInt(session.metadata?.credits, 10);

      if (!email) {
        console.error('SideKix [website credits claim] no email on session', session.id);
      } else if (!Number.isInteger(credits) || credits <= 0) {
        console.error('SideKix [website credits claim] missing/invalid credits metadata on session', session.id);
      } else {
        try {
          const claimRes = await fetch(
            'https://api.sidekixhq.com/internal/website-credits/claims',
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'x-internal-key': process.env.WEBSITE_INTERNAL_KEY || '',
              },
              body: JSON.stringify({ sessionId: session.id, email, credits }),
            },
          );
          if (!claimRes.ok) {
            const body = await claimRes.text().catch(() => '');
            throw new Error(`Admin-Backend responded ${claimRes.status}: ${body}`);
          }
        } catch (err) {
          console.error('SideKix [website credits claim] failed:', err);
          res.status(502).json({ error: 'Could not record credits claim, will retry' });
          return;
        }
      }
    }
  }

  res.status(200).json({ received: true });
};
