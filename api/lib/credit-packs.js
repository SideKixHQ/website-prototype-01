const DEFAULT_PACK = 'medium';
const PACK_KEYS = ['small', 'medium', 'large'];

function creditPacks(pricing) {
  const listed = Array.isArray(pricing && pricing.kixCreditPacks) ? pricing.kixCreditPacks : [];
  const out = [];
  for (const key of PACK_KEYS) {
    const source = key === DEFAULT_PACK
      ? pricing && pricing.standardBundle
      : listed.find((p) => p && p.key === key);
    const credits = source && Number(source.credits);
    const priceCents = source && Math.round(Number(source.priceUSD) * 100);
    if (Number.isInteger(credits) && credits > 0 && Number.isInteger(priceCents) && priceCents > 0) {
      out.push({ key, credits, priceCents });
    }
  }
  return out;
}

function resolveCreditPack(pricing, key) {
  const wanted = key === undefined || key === null || key === '' ? DEFAULT_PACK : key;
  return creditPacks(pricing).find((p) => p.key === wanted) || null;
}

module.exports = { creditPacks, resolveCreditPack, DEFAULT_PACK, PACK_KEYS };
