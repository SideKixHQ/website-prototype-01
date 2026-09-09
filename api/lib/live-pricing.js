// Single source of truth for what to actually charge — fetched from
// Admin-Backend rather than hardcoded, closing a gap a payments audit found:
// the credits price ($19/350) and membership tier prices were each hardcoded
// independently here, in Admin-Backend, and in the iOS app, with nothing but
// a comment keeping them in agreement. The real charge was always computed
// server-side regardless (this was a display-drift risk, not a
// billing-integrity one) — this makes the website's copy of "server-side"
// mean the same live number Admin-Backend actually uses.
//
// Cached in module scope with a short TTL rather than fetched on every
// request: a serverless function instance is reused across warm invocations,
// and coupling every checkout attempt to Admin-Backend being reachable at
// that exact moment would make a payments-adjacent outage there also break
// purchases here, for no real benefit over a price that's at most a few
// minutes stale. Falls back to the last hardcoded-known-good values only if
// the live fetch fails AND nothing is cached yet — a transient network blip
// shouldn't hard-fail checkout, but a persistently unreachable backend means
// falling back to numbers that could themselves be stale, which is the same
// risk this module exists to close. That tradeoff is deliberate: availability
// over perfect freshness, once at least one real fetch has ever succeeded.

const ADMIN_BACKEND_BASE = 'https://api.sidekixhq.com';
const CACHE_TTL_MS = 5 * 60 * 1000;

// Emergency fallback only — used solely if the very first fetch this
// instance ever makes fails. Update these if the real price changes and
// you want new instances to fail safe with the right number, but they are
// not the source of truth; memberships/credits-pricing and memberships/plans
// on Admin-Backend are.
const FALLBACK_CREDITS_PRICING = {
  pricePerCredit: 19 / 350,
  standardBundle: { credits: 350, priceUSD: 19 },
};
const FALLBACK_MEMBERSHIP_PLANS = {
  access: { name: 'Access', monthlyUsdCents: 3900 },
  core: { name: 'Core', monthlyUsdCents: 9900 },
  premium: { name: 'Premium', monthlyUsdCents: 29900 },
};

let creditsPricingCache = null; // { value, fetchedAt }
let membershipPlansCache = null; // { value, fetchedAt }

async function fetchFromAdminBackend(path) {
  const res = await fetch(`${ADMIN_BACKEND_BASE}${path}`, {
    headers: {
      // Admin-Backend's global DeviceIdGuard requires this on every route
      // not explicitly exempted (admin/otp/rbac/uploads/payments) —
      // /memberships/* is not one of the exemptions.
      'x-device-agent': 'web',
    },
  });
  if (!res.ok) {
    throw new Error(`Admin-Backend responded ${res.status} for ${path}`);
  }
  return res.json();
}

function isFresh(entry) {
  return !!entry && Date.now() - entry.fetchedAt < CACHE_TTL_MS;
}

async function getCreditsPricing() {
  if (isFresh(creditsPricingCache)) return creditsPricingCache.value;
  try {
    const value = await fetchFromAdminBackend('/memberships/credits-pricing');
    creditsPricingCache = { value, fetchedAt: Date.now() };
    return value;
  } catch (err) {
    console.error('live-pricing: could not fetch credits pricing, falling back:', err);
    return creditsPricingCache ? creditsPricingCache.value : FALLBACK_CREDITS_PRICING;
  }
}

async function getMembershipPlans() {
  if (isFresh(membershipPlansCache)) return membershipPlansCache.value;
  try {
    const plans = await fetchFromAdminBackend('/memberships/plans');
    // Reshape the array response into the { slug: { name, monthlyUsdCents } }
    // map create-checkout-session.js already expects, so nothing downstream
    // needs to know this used to be a hardcoded object literal.
    const bySlug = {};
    for (const plan of plans) {
      if (!plan || !plan.slug) continue;
      bySlug[plan.slug] = {
        name: plan.name,
        monthlyUsdCents: Math.round(Number(plan.pricePerMonth) * 100),
      };
    }
    membershipPlansCache = { value: bySlug, fetchedAt: Date.now() };
    return bySlug;
  } catch (err) {
    console.error('live-pricing: could not fetch membership plans, falling back:', err);
    return membershipPlansCache ? membershipPlansCache.value : FALLBACK_MEMBERSHIP_PLANS;
  }
}

module.exports = { getCreditsPricing, getMembershipPlans };
