// A publishable key is safe to expose client-side by design (that's the
// whole point of the pk_/sk_ split) — this endpoint exists so checkout.html
// can fetch it from the one place it's configured (STRIPE_PUBLISHABLE_KEY,
// same as create-payment-intent.js) rather than hardcoding it a second time
// in static HTML, which would silently drift the moment the key rotates.
// Called at page load, well before the user finishes typing an email, so
// the Card Element can mount the instant they submit instead of waiting on
// this network round trip too.
module.exports = async (req, res) => {
  res.status(200).json({ publishableKey: process.env.STRIPE_PUBLISHABLE_KEY || null });
};
