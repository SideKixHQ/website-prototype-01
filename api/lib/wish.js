// The falling-star offer on membership.html: 10% off the locked membership
// rate, for life, if the rate is locked within 24 hours of catching the star.
//
// The 24 hours is enforced here, not in the browser: catching the star asks
// /api/wish for a token that carries its own expiry, signed with
// WISH_SIGNING_KEY (a Vercel environment variable). Checkout only applies the
// discount to a token that verifies and has not expired. Without the key the
// offer is switched off everywhere: /api/wish reports it disabled, the star
// does not fly, and checkout refuses any token, so the site never promises a
// discount it cannot check.
//
// "For life" needs nothing extra: the discount is baked into the locked
// monthly rate sent to Admin-Backend, which charges and renews at that rate.
const crypto = require('crypto');

const WISH_CODE = 'SIDEKIX-WISH';
const WISH_PERCENT = 10;
const WINDOW_MS = 24 * 60 * 60 * 1000;

function signingKey() {
  return process.env.WISH_SIGNING_KEY || '';
}

function enabled() {
  return signingKey().length >= 32;
}

function mac(body) {
  return crypto.createHmac('sha256', signingKey()).update(body).digest('base64url');
}

function issue(now = Date.now()) {
  if (!enabled()) return null;
  const expiresAt = now + WINDOW_MS;
  const body = Buffer.from(JSON.stringify({ v: 1, iat: now, exp: expiresAt })).toString('base64url');
  return { token: `${body}.${mac(body)}`, expiresAt };
}

function verify(token, now = Date.now()) {
  if (!enabled()) return { ok: false, reason: 'disabled' };
  if (typeof token !== 'string' || token.length > 512) return { ok: false, reason: 'invalid' };
  const parts = token.split('.');
  if (parts.length !== 2) return { ok: false, reason: 'invalid' };
  const [body, sig] = parts;
  const expected = Buffer.from(mac(body));
  const given = Buffer.from(sig);
  if (expected.length !== given.length || !crypto.timingSafeEqual(expected, given)) {
    return { ok: false, reason: 'invalid' };
  }
  let payload;
  try {
    payload = JSON.parse(Buffer.from(body, 'base64url').toString('utf8'));
  } catch (err) {
    return { ok: false, reason: 'invalid' };
  }
  if (!payload || payload.v !== 1 || !Number.isFinite(payload.exp)) return { ok: false, reason: 'invalid' };
  if (payload.exp <= now) return { ok: false, reason: 'expired' };
  return { ok: true, expiresAt: payload.exp, issuedAt: payload.iat };
}

function discounted(cents) {
  return Math.round((cents * (100 - WISH_PERCENT)) / 100);
}

module.exports = { WISH_CODE, WISH_PERCENT, WINDOW_MS, enabled, issue, verify, discounted };
