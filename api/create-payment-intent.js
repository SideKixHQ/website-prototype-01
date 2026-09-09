const Stripe = require('stripe');

// Mirrors create-checkout-session.js's credits pricing exactly — kept in
// sync with CreditsFeature.Bundle.bundlePriceUSD ($19/350 credits, flat per
// pack) on the iOS side. Only credits are supported here: this endpoint
// backs the embedded/animated Payment Element checkout, which — for now —
// is a credits-only experience (see membership.html). Membership rate-lock
// pre-orders still go through the redirect-based create-checkout-session.js.
const CREDIT_PACK_USD_CENTS = 1900;
const CREDIT_PACK_SIZE = 350;
const MAX_PACKS = 10;

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const email = typeof req.body?.email === 'string' ? req.body.email.trim() : '';
  if (!email || !email.includes('@')) {
    res.status(400).json({ error: 'A valid email is required' });
    return;
  }

  const packs = Math.min(MAX_PACKS, Math.max(1, parseInt(req.body?.packs, 10) || 1));
  const amount = packs * CREDIT_PACK_USD_CENTS;
  const credits = packs * CREDIT_PACK_SIZE;

  try {
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2026-07-29.dahlia',
    });
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency: 'usd',
      // Card is enough for a $19-$190 impulse purchase, and it's what makes
      // `redirect: 'if_required'` reliable client-side — several other
      // automatic payment methods redirect the browser away regardless of
      // that flag, which would silently break the "stay on page, animate
      // success" point of this whole embedded flow.
      payment_method_types: ['card'],
      receipt_email: email,
      // Stored in metadata (not just receipt_email) because
      // stripe-webhook.js's payment_intent.succeeded handler reads
      // everything it needs straight off the PaymentIntent — same shape
      // create-checkout-session.js already stores on the Checkout Session.
      metadata: { source: 'website', type: 'credits', packs: String(packs), credits: String(credits), email },
    });

    res.status(200).json({
      clientSecret: paymentIntent.client_secret,
      publishableKey: process.env.STRIPE_PUBLISHABLE_KEY,
      amount,
      credits,
    });
  } catch (err) {
    console.error('create-payment-intent failed:', err);
    res.status(500).json({ error: 'Could not start checkout. Please try again.' });
  }
};
