const { getCreditsPricing } = require('./lib/live-pricing');
const { creditPacks } = require('./lib/credit-packs');

module.exports = async (req, res) => {
  const packs = creditPacks(await getCreditsPricing()).map((p) => ({
    key: p.key,
    credits: p.credits,
    priceUSD: p.priceCents / 100,
  }));
  res.setHeader('Cache-Control', 'public, max-age=300');
  res.status(200).json({ packs });
};
