const Stripe = require('stripe');
const { creditsTaxCode } = require('./lib/credits-tax');
const { getCreditsPricing, getMembershipPlans } = require('./lib/live-pricing');
const { resolveCreditPack } = require('./lib/credit-packs');
const wish = require('./lib/wish');
const { isSalesTaxEnabled } = require('./lib/sales-tax');

// Server-defined pricing only — the client sends an identifier (plan/packs),
// never an amount. Fetched live from Admin-Backend (see lib/live-pricing.js)
// rather than hardcoded, so the website can never quote a number the app
// itself wouldn't charge — that used to be enforced only by a comment.
const MAX_PACKS = 10;

function randomSuffix(length) {
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  let out = '';
  for (let i = 0; i < length; i++) {
    out += letters[Math.floor(Math.random() * letters.length)];
  }
  return out;
}

async function taxedLineItem(stripe, item) {
  return {
    ...item,
    price_data: {
      ...item.price_data,
      tax_behavior: 'exclusive',
      product_data: { ...item.price_data.product_data, tax_code: await creditsTaxCode(stripe) },
    },
  };
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
  let membership = null;

  if (type === 'credits') {
    const packs = Math.min(MAX_PACKS, Math.max(1, parseInt(req.body.packs, 10) || 1));
    const pricing = await getCreditsPricing();
    if (!pricing) {
      res.status(503).json({ error: "Kix Credit prices couldn't be loaded. Please try again in a moment.", code: 'pricing_unavailable' });
      return;
    }
    const pack = resolveCreditPack(pricing, req.body.pack);
    if (!pack) {
      res.status(400).json({ error: 'That credit pack is not available', code: 'unknown_pack' });
      return;
    }
    lineItem = {
      price_data: {
        currency: 'usd',
        product_data: {
          name: 'Kix Credits',
          description: `${pack.credits} credits per pack`,
        },
        unit_amount: pack.priceCents,
      },
      quantity: packs,
    };
    successUrl = `${origin}/membership.html?purchased=1&pack=${pack.key}&packs=${packs}&session_id={CHECKOUT_SESSION_ID}`;
    cancelUrl = `${origin}/membership.html`;
    // credits is stored explicitly (not just packs) so the webhook never
    // has to independently recompute the bundle size — one live source,
    // fetched once above.
    metadata = { source: 'website', type: 'credits', pack: pack.key, packs: String(packs), credits: String(packs * pack.credits) };
  } else if (type === 'membership') {
    // A membership rate lock (James, 2026-10-15): the card is saved and
    // nothing is charged. Admin-Backend records the lock from the webhook,
    // lists it in the admin panel, and when the tier goes live charges the
    // locked rate and grants the membership in the app, then renews at that
    // same rate. So the falling-star 10% is simply a lower locked rate.
    const plans = await getMembershipPlans();
    const planSlug = req.body.plan;
    const plan = plans[planSlug];
    if (!plan) {
      res.status(400).json({ error: 'Unknown plan' });
      return;
    }
    let lockedCents = plan.monthlyUsdCents;
    let promoCode = null;
    if (req.body.wish) {
      const check = wish.verify(req.body.wish);
      if (!check.ok) {
        res.status(400).json({ error: check.reason === 'expired' ? 'offer_expired' : 'offer_invalid' });
        return;
      }
      lockedCents = wish.discounted(plan.monthlyUsdCents);
      promoCode = wish.WISH_CODE;
    }
    membership = { planSlug, planName: plan.name, lockedCents, listCents: plan.monthlyUsdCents, promoCode };
    successUrl = `${origin}/join.html?reserved=1&plan=${planSlug}&locked=${lockedCents}&session_id={CHECKOUT_SESSION_ID}`;
    cancelUrl = `${origin}/join.html?plan=${planSlug}&intent=prepay`;
    metadata = {
      source: 'website',
      type: 'membership_rate_lock',
      plan: planSlug,
      lockedMonthlyUsdCents: String(lockedCents),
      listMonthlyUsdCents: String(plan.monthlyUsdCents),
      ...(promoCode ? { promoCode } : {}),
    };
  } else {
    res.status(400).json({ error: 'Unknown purchase type' });
    return;
  }

  const email = typeof req.body.email === 'string' ? req.body.email.trim() : undefined;

  const dollars = (cents) => `$${(cents / 100).toFixed(2).replace(/\.00$/, '')}`;

  // Shown on the Stripe-hosted checkout page itself (checkout.stripe.com),
  // not on our site, so it is the only copy a buyer sees between clicking
  // through and confirming. It has to say plainly what happens to the card.
  const submitMessage = type === 'credits'
    ? 'Kix turns your goals and challenges into a personalized path forward. Kix Credits are yours the moment you buy them. Kix Credits are not refundable and do not expire.'
    : `Nothing is charged today. When SideKix ${membership.planName} goes live, this card is charged ${dollars(membership.lockedCents)} a month, your locked rate${membership.promoCode ? ` with ${wish.WISH_PERCENT}% off for life` : ''}, for as long as you stay a member. Memberships are not refundable.`;

  const sharedText = {
    consent_collection: {
      terms_of_service: 'required',
    },
    custom_text: {
      submit: {
        message: submitMessage,
      },
      terms_of_service_acceptance: {
        message: `I agree to the [SideKix Purchase and Payment Policy](${origin}/purchase-policy.html).`,
      },
    },
  };

  const creditsTaxed = type === 'credits' && isSalesTaxEnabled();

  try {
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2026-07-29.dahlia',
    });
    const session = membership
      ? await stripe.checkout.sessions.create({
          mode: 'setup',
          payment_method_types: ['card'],
          customer_creation: 'always',
          success_url: successUrl,
          cancel_url: cancelUrl,
          metadata,
          setup_intent_data: {
            description: `SideKix ${membership.planName} rate lock: ${dollars(membership.lockedCents)} a month, charged when the tier goes live`,
            metadata,
          },
          ...(email ? { customer_email: email } : {}),
          integration_identifier: `sidekix-website-${randomSuffix(8)}`,
          ...sharedText,
        })
      : await stripe.checkout.sessions.create({
          mode: 'payment',
          line_items: [creditsTaxed ? await taxedLineItem(stripe, lineItem) : lineItem],
          success_url: successUrl,
          cancel_url: cancelUrl,
          metadata,
          ...(creditsTaxed ? { automatic_tax: { enabled: true }, billing_address_collection: 'required' } : {}),
          ...(email ? { customer_email: email } : {}),
          integration_identifier: `sidekix-website-${randomSuffix(8)}`,
          ...sharedText,
        });

    res.status(200).json({ url: session.url });
  } catch (err) {
    console.error('create-checkout-session failed:', err);
    res.status(500).json({ error: 'Could not start checkout. Please try again.' });
  }
};
