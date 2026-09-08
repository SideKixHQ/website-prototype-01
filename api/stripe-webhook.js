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
      // Set only when autoTop was checked — a card was saved against this
      // Stripe Customer for later, but nothing charges it automatically yet.
      // The consent fields are the record terms.html §21.10 requires for
      // this express authorization: when it was given and under which
      // version of the terms.
      autoTopRequested: session.metadata?.autoTopRequested === 'true',
      autoTopConsentAt: session.metadata?.autoTopConsentAt || null,
      autoTopConsentTermsVersion: session.metadata?.autoTopConsentTermsVersion || null,
      stripeCustomerId: session.customer || null,
    });
  }

  res.status(200).json({ received: true });
};
