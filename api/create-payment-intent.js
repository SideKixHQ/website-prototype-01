const Stripe = require('stripe');
const { getCreditsPricing } = require('./lib/live-pricing');
const { resolveCreditPack } = require('./lib/credit-packs');
const { isSalesTaxEnabled } = require('./lib/sales-tax');
const { creditsTaxCode, normalizePostalCode } = require('./lib/credits-tax');

// Fetched live from Admin-Backend (see lib/live-pricing.js), same as
// create-checkout-session.js — previously this hardcoded its own separate
// copy of the credits price with only a comment keeping it in sync. Only
// credits are supported here: this endpoint backs the embedded/animated
// Payment Element checkout, which — for now — is a credits-only experience
// (see membership.html). Membership rate-lock pre-orders still go through
// the redirect-based create-checkout-session.js.
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

  const taxed = isSalesTaxEnabled();
  const postalCode = taxed ? normalizePostalCode(req.body?.postalCode) : null;
  if (taxed && !postalCode) {
    res.status(400).json({ error: 'A valid ZIP code is required', code: 'postal_code_required' });
    return;
  }

  const packs = Math.min(MAX_PACKS, Math.max(1, parseInt(req.body?.packs, 10) || 1));
  const pack = resolveCreditPack(await getCreditsPricing(), req.body?.pack);
  if (!pack) {
    res.status(400).json({ error: 'That credit pack is not available', code: 'unknown_pack' });
    return;
  }
  const subtotal = packs * pack.priceCents;
  const credits = packs * pack.credits;

  try {
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2026-07-29.dahlia',
    });
    let amount = subtotal;
    let tax = 0;
    let taxMetadata = {};
    if (taxed) {
      const calculation = await stripe.tax.calculations.create({
        currency: 'usd',
        customer_details: {
          address: { country: 'US', postal_code: postalCode },
          address_source: 'billing',
        },
        line_items: [
          {
            amount: subtotal,
            quantity: 1,
            reference: 'credits',
            tax_code: await creditsTaxCode(stripe),
            tax_behavior: 'exclusive',
          },
        ],
      });
      amount = calculation.amount_total;
      tax = calculation.tax_amount_exclusive;
      taxMetadata = {
        taxCalculationId: calculation.id,
        subtotalCents: String(subtotal),
        taxCents: String(tax),
        postalCode,
      };
    }
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
      metadata: { source: 'website', type: 'credits', pack: pack.key, packs: String(packs), credits: String(credits), email, ...taxMetadata },
    });

    res.status(200).json({
      clientSecret: paymentIntent.client_secret,
      publishableKey: process.env.STRIPE_PUBLISHABLE_KEY,
      amount,
      subtotal,
      tax,
      credits,
    });
  } catch (err) {
    console.error('create-payment-intent failed:', err);
    res.status(500).json({ error: 'Could not start checkout. Please try again.' });
  }
};
