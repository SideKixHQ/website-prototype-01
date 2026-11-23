const test = require('node:test');
const assert = require('node:assert');
const path = require('path');

const API = path.resolve(__dirname, '..', 'api');
const { creditPacks, resolveCreditPack } = require(path.join(API, 'lib', 'credit-packs.js'));

const NEW_BACKEND = {
  standardBundle: { credits: 350, priceUSD: 19.99 },
  kixCreditPacks: [
    { key: 'small', credits: 150, priceUSD: 9.99 },
    { key: 'medium', credits: 350, priceUSD: 19.99 },
    { key: 'large', credits: 750, priceUSD: 39.99 },
  ],
};
const OLD_BACKEND = { standardBundle: { credits: 350, priceUSD: 19 } };

test('lists Small, Medium and Large when the backend publishes them', () => {
  assert.deepStrictEqual(creditPacks(NEW_BACKEND), [
    { key: 'small', credits: 150, priceCents: 999 },
    { key: 'medium', credits: 350, priceCents: 1999 },
    { key: 'large', credits: 750, priceCents: 3999 },
  ]);
});

test('an older backend sells only the Medium pack, at its own price', () => {
  assert.deepStrictEqual(creditPacks(OLD_BACKEND), [{ key: 'medium', credits: 350, priceCents: 1900 }]);
  assert.strictEqual(resolveCreditPack(OLD_BACKEND, 'small'), null);
  assert.strictEqual(resolveCreditPack(OLD_BACKEND, 'large'), null);
});

test('no pack means Medium, and an unknown or malformed pack is refused', () => {
  assert.strictEqual(resolveCreditPack(NEW_BACKEND, undefined).key, 'medium');
  assert.strictEqual(resolveCreditPack(NEW_BACKEND, '').key, 'medium');
  assert.strictEqual(resolveCreditPack(NEW_BACKEND, 'huge'), null);
  assert.strictEqual(resolveCreditPack(NEW_BACKEND, '__proto__'), null);
  const broken = { ...NEW_BACKEND, kixCreditPacks: [{ key: 'small', credits: 0, priceUSD: 9.99 }, { key: 'large', credits: 750 }] };
  assert.deepStrictEqual(creditPacks(broken).map((p) => p.key), ['medium']);
});

test('the payment APIs charge the pack the server knows, never a client amount', async () => {
  const intents = [];
  const sessions = [];
  const stripeId = require.resolve('stripe');
  const pricingId = require.resolve(path.join(API, 'lib', 'live-pricing.js'));
  const saved = { stripe: require.cache[stripeId], pricing: require.cache[pricingId] };
  require.cache[stripeId] = {
    id: stripeId, filename: stripeId, loaded: true,
    exports: function FakeStripe() {
      return {
        paymentIntents: { create: async (p) => { intents.push(p); return { id: 'pi_t', client_secret: 's' }; } },
        checkout: { sessions: { create: async (p) => { sessions.push(p); return { url: 'https://checkout.stripe.test/s' }; } } },
        products: { retrieve: async (id) => ({ id, tax_code: 'txcd_10103000' }) },
      };
    },
  };
  require.cache[pricingId] = {
    id: pricingId, filename: pricingId, loaded: true,
    exports: { getCreditsPricing: async () => NEW_BACKEND, getMembershipPlans: async () => ({}) },
  };
  for (const m of ['create-payment-intent.js', 'create-checkout-session.js', 'credit-packs.js']) {
    delete require.cache[require.resolve(path.join(API, m))];
  }
  const before = process.env.SALES_TAX_ENABLED;
  delete process.env.SALES_TAX_ENABLED;
  try {
    const paymentIntent = require(path.join(API, 'create-payment-intent.js'));
    const checkoutSession = require(path.join(API, 'create-checkout-session.js'));
    const listing = require(path.join(API, 'credit-packs.js'));
    const res = () => ({ code: 200, body: null, headers: {}, status(c) { this.code = c; return this; }, json(b) { this.body = b; return this; }, setHeader(k, v) { this.headers[k] = v; } });
    const post = async (h, body) => { const r = res(); await h({ method: 'POST', headers: { origin: 'https://sidekixhq.com' }, body }, r); return r; };

    const large = await post(paymentIntent, { pack: 'large', packs: 2, email: 'a@b.co', amount: 1 });
    assert.strictEqual(large.code, 200);
    assert.strictEqual(intents[0].amount, 7998);
    assert.deepStrictEqual(
      [intents[0].metadata.pack, intents[0].metadata.packs, intents[0].metadata.credits],
      ['large', '2', '1500'],
    );

    const medium = await post(paymentIntent, { packs: 1, email: 'a@b.co' });
    assert.strictEqual(medium.code, 200);
    assert.strictEqual(intents[1].amount, 1999);
    assert.strictEqual(intents[1].metadata.pack, 'medium');

    const unknown = await post(paymentIntent, { pack: 'huge', packs: 1, email: 'a@b.co' });
    assert.strictEqual(unknown.code, 400);
    assert.strictEqual(unknown.body.code, 'unknown_pack');
    assert.strictEqual(intents.length, 2);

    const small = await post(checkoutSession, { type: 'credits', pack: 'small', packs: 3 });
    assert.strictEqual(small.code, 200);
    assert.strictEqual(sessions[0].line_items[0].price_data.unit_amount, 999);
    assert.strictEqual(sessions[0].line_items[0].quantity, 3);
    assert.deepStrictEqual([sessions[0].metadata.pack, sessions[0].metadata.credits], ['small', '450']);
    assert.match(sessions[0].success_url, /pack=small&packs=3/);

    const r = res();
    await listing({ method: 'GET' }, r);
    assert.deepStrictEqual(r.body.packs.map((p) => [p.key, p.credits, p.priceUSD]), [
      ['small', 150, 9.99], ['medium', 350, 19.99], ['large', 750, 39.99],
    ]);
  } finally {
    if (before === undefined) delete process.env.SALES_TAX_ENABLED; else process.env.SALES_TAX_ENABLED = before;
    if (saved.stripe) require.cache[stripeId] = saved.stripe; else delete require.cache[stripeId];
    if (saved.pricing) require.cache[pricingId] = saved.pricing; else delete require.cache[pricingId];
  }
});

test('no live price means no checkout and no listed packs, never a built-in price', async () => {
  const intents = [];
  const sessions = [];
  const stripeId = require.resolve('stripe');
  const pricingId = require.resolve(path.join(API, 'lib', 'live-pricing.js'));
  const saved = { stripe: require.cache[stripeId], pricing: require.cache[pricingId] };
  require.cache[stripeId] = {
    id: stripeId, filename: stripeId, loaded: true,
    exports: function FakeStripe() {
      return {
        paymentIntents: { create: async (p) => { intents.push(p); return { id: 'pi_t', client_secret: 's' }; } },
        checkout: { sessions: { create: async (p) => { sessions.push(p); return { url: 'https://checkout.stripe.test/s' }; } } },
        products: { retrieve: async (id) => ({ id, tax_code: 'txcd_10103000' }) },
      };
    },
  };
  const realFetch = global.fetch;
  const realError = console.error;
  global.fetch = async () => { throw new Error('offline'); };
  console.error = () => {};
  delete require.cache[pricingId];
  for (const m of ['create-payment-intent.js', 'create-checkout-session.js', 'credit-packs.js']) {
    delete require.cache[require.resolve(path.join(API, m))];
  }
  const before = process.env.SALES_TAX_ENABLED;
  delete process.env.SALES_TAX_ENABLED;
  try {
    const paymentIntent = require(path.join(API, 'create-payment-intent.js'));
    const checkoutSession = require(path.join(API, 'create-checkout-session.js'));
    const listing = require(path.join(API, 'credit-packs.js'));
    const res = () => ({ code: 200, body: null, headers: {}, status(c) { this.code = c; return this; }, json(b) { this.body = b; return this; }, setHeader(k, v) { this.headers[k] = v; } });
    const post = async (h, body) => { const r = res(); await h({ method: 'POST', headers: { origin: 'https://sidekixhq.com' }, body }, r); return r; };

    const intent = await post(paymentIntent, { pack: 'medium', packs: 1, email: 'a@b.co' });
    assert.strictEqual(intent.code, 503);
    assert.strictEqual(intent.body.code, 'pricing_unavailable');
    assert.ok(intent.body.error);

    const session = await post(checkoutSession, { type: 'credits', packs: 1 });
    assert.strictEqual(session.code, 503);
    assert.strictEqual(session.body.code, 'pricing_unavailable');

    assert.strictEqual(intents.length, 0);
    assert.strictEqual(sessions.length, 0);

    const r = res();
    await listing({ method: 'GET' }, r);
    assert.deepStrictEqual(r.body.packs, []);
    assert.strictEqual(r.headers['Cache-Control'], 'no-store');
  } finally {
    global.fetch = realFetch;
    console.error = realError;
    if (before === undefined) delete process.env.SALES_TAX_ENABLED; else process.env.SALES_TAX_ENABLED = before;
    if (saved.stripe) require.cache[stripeId] = saved.stripe; else delete require.cache[stripeId];
    if (saved.pricing) require.cache[pricingId] = saved.pricing; else delete require.cache[pricingId];
  }
});
