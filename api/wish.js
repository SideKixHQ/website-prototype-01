// GET  /api/wish  -> { enabled }            membership.html asks before the star flies
// POST /api/wish  -> { token, expiresAt }   catching the star starts its 24 hours
const wish = require('./lib/wish');

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'GET') {
    res.status(200).json({ enabled: wish.enabled(), percent: wish.WISH_PERCENT });
    return;
  }
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  const issued = wish.issue();
  if (!issued) {
    res.status(503).json({ error: 'offer_disabled' });
    return;
  }
  res.status(200).json(issued);
};
