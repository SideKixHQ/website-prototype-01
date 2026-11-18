const CREDITS_PRODUCT_ID = 'prod_V977UwyMv8Wj50';
const FALLBACK_TAX_CODE = 'txcd_10103000';
const TTL_MS = 10 * 60 * 1000;
const ERROR_TTL_MS = 60 * 1000;

let cached = null;

function creditsProductId(env = process.env) {
  return (env.STRIPE_CREDITS_PRODUCT_ID || CREDITS_PRODUCT_ID).trim();
}

async function creditsTaxCode(stripe, now = Date.now) {
  const id = creditsProductId();
  if (cached && cached.id === id && cached.expiresAt > now()) return cached.taxCode;
  try {
    const product = await stripe.products.retrieve(id);
    const raw = product && product.tax_code;
    const taxCode = (typeof raw === 'string' ? raw : raw && raw.id) || FALLBACK_TAX_CODE;
    cached = { id, taxCode, expiresAt: now() + TTL_MS };
    return taxCode;
  } catch (err) {
    console.error(`credits-tax: could not read Stripe product ${id}, using ${FALLBACK_TAX_CODE}:`, err.message);
    cached = { id, taxCode: FALLBACK_TAX_CODE, expiresAt: now() + ERROR_TTL_MS };
    return FALLBACK_TAX_CODE;
  }
}

function resetCreditsTaxCodeCache() {
  cached = null;
}

const US_POSTAL_CODE = /^\d{5}(-\d{4})?$/;

function normalizePostalCode(value) {
  const zip = typeof value === 'string' ? value.trim() : '';
  return US_POSTAL_CODE.test(zip) ? zip : null;
}

module.exports = { creditsTaxCode, creditsProductId, resetCreditsTaxCodeCache, normalizePostalCode, FALLBACK_TAX_CODE };
