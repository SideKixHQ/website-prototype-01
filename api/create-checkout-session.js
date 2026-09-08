const Stripe = require('stripe');

// Server-defined pricing only — the client sends an identifier (plan/packs),
// never an amount. Mirrors the iOS app's real prices exactly:
// CreditsFeature.Bundle.bundlePriceUSD ($19/350 credits, flat per pack) and
// MembershipHubFeature's monthly tiers, so the website can never quote a
// number the app itself wouldn't charge.
const CREDIT_PACK_USD_CENTS = 1900;
const CREDIT_PACK_SIZE = 350;
const MAX_PACKS = 10;

const MEMBERSHIP_PLANS = {
  access: { name: 'Access', monthlyUsdCents: 3900 },
  core: { name: 'Core', monthlyUsdCents: 9900 },
  premium: { name: 'Premium', monthlyUsdCents: 29900 },
};

function randomSuffix(length) {
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  let out = '';
  for (let i = 0; i < length; i++) {
    out += letters[Math.floor(Math.random() * letters.length)];
  }
  return out;
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const origin = req.headers.origin || `https://${req.headers.host}`;
  const { type } = req.body || {};

  let lineItem;
  let successUrl;
  let cancelUrl;
  let metadata;

  if (type === 'credits') {
    const packs = Math.min(MAX_PACKS, Math.max(1, parseInt(req.body.packs, 10) || 1));
    lineItem = {
      price_data: {
        currency: 'usd',
        product_data: {
          name: 'Kix Credits',
          description: `${CREDIT_PACK_SIZE} credits per pack`,
        },
        unit_amount: CREDIT_PACK_USD_CENTS,
      },
      quantity: packs,
    };
    successUrl = `${origin}/membership.html?purchased=1&packs=${packs}&session_id={CHECKOUT_SESSION_ID}`;
    cancelUrl = `${origin}/membership.html`;
    metadata = { source: 'website', type: 'credits', packs: String(packs) };
  } else if (type === 'membership') {
    const plan = MEMBERSHIP_PLANS[req.body.plan];
    if (!plan) {
      res.status(400).json({ error: 'Unknown plan' });
      return;
    }
    lineItem = {
      price_data: {
        currency: 'usd',
        product_data: {
          name: `SideKix ${plan.name} — rate lock`,
          description: 'One-time pre-order to lock in this monthly rate. Recurring billing starts when this tier goes live.',
        },
        unit_amount: plan.monthlyUsdCents,
      },
      quantity: 1,
    };
    successUrl = `${origin}/join.html?reserved=1&plan=${req.body.plan}&session_id={CHECKOUT_SESSION_ID}`;
    cancelUrl = `${origin}/join.html?plan=${req.body.plan}&intent=prepay`;
    metadata = { source: 'website', type: 'membership', plan: req.body.plan };
  } else {
    res.status(400).json({ error: 'Unknown purchase type' });
    return;
  }

  const email = typeof req.body.email === 'string' ? req.body.email.trim() : undefined;

  try {
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2026-07-29.dahlia',
    });
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [lineItem],
      success_url: successUrl,
      cancel_url: cancelUrl,
      metadata,
      ...(email ? { customer_email: email } : {}),
      integration_identifier: `sidekix-website-${randomSuffix(8)}`,
    });

    res.status(200).json({ url: session.url });
  } catch (err) {
    console.error('create-checkout-session failed:', err);
    res.status(500).json({ error: 'Could not start checkout. Please try again.' });
  }
};
