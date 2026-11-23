const { getCreditsPricing } = require('./lib/live-pricing');
const { creditPacks } = require('./lib/credit-packs');

module.exports = async (req, res) => {
  const pricing = await getCreditsPricing();
  const packs = creditPacks(pricing).map((p) => ({
    key: p.key,
    credits: p.credits,
    priceUSD: p.priceCents / 100,
  }));
  res.setHeader('Cache-Control', pricing ? 'public, max-age=300' : 'no-store');
  res.status(200).json({ packs });
};
