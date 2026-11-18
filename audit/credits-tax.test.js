const test = require('node:test');
const assert = require('node:assert');
const path = require('path');
const { Readable } = require('stream');

const API = path.resolve(__dirname, '..', 'api');
const calls = {};
let productTaxCode = 'txcd_10103101';
let productFails = false;
let transactionError = null;

function reset() {
  for (const k of ['sessions', 'intents', 'calculations', 'transactions', 'products', 'fetches']) calls[k] = [];
  productTaxCode = 'txcd_10103101';
  productFails = false;
  transactionError = null;
  require(path.join(API, 'lib', 'credits-tax.js')).resetCreditsTaxCodeCache();
}

function FakeStripe() {
  return {
    checkout: {
      sessions: {
        create: async (p) => { calls.sessions.push(p); return { url: 'https://checkout.stripe.test/s' }; },
      },
    },
    paymentIntents: {
      create: async (p) => { calls.intents.push(p); return { id: 'pi_test', client_secret: 'pi_test_secret' }; },
    },
    products: {
      retrieve: async (id) => {
        calls.products.push(id);
        if (productFails) throw new Error('No such product');
        return { id, tax_code: productTaxCode };
      },
    },
    tax: {
      calculations: {
        create: async (p) => {
          calls.calculations.push(p);
          const tax = Math.round(p.line_items[0].amount * 0.0475);
          return { id: 'taxcalc_1', amount_total: p.line_items[0].amount + tax, tax_amount_exclusive: tax };
        },
      },
      transactions: {
        createFromCalculation: async (p, opts) => {
          calls.transactions.push({ p, opts });
          if (transactionError) throw transactionError;
          return { id: 'tax_txn_1' };
        },
      },
    },
  };
}
FakeStripe.webhooks = { constructEvent: (raw) => JSON.parse(raw.toString()) };

function stub(modulePath, exports) {
  const id = require.resolve(modulePath);
  require.cache[id] = { id, filename: id, loaded: true, exports };
}
stub('stripe', FakeStripe);
stub(path.join(API, 'lib', 'live-pricing.js'), {
  getCreditsPricing: async () => ({ standardBundle: { credits: 350, priceUSD: 19 } }),
  getMembershipPlans: async () => ({ core: { name: 'Core', monthlyUsdCents: 9900 } }),
});

global.fetch = async (url, init) => {
  calls.fetches.push({ url, body: JSON.parse(init.body) });
  return { ok: true, status: 200, text: async () => '', json: async () => ({}) };
};

const checkoutSession = require(path.join(API, 'create-checkout-session.js'));
const paymentIntent = require(path.join(API, 'create-payment-intent.js'));
const stripeConfig = require(path.join(API, 'stripe-config.js'));
const webhook = require(path.join(API, 'stripe-webhook.js'));

function fakeRes() {
  return {
    code: 200,
    body: null,
    status(c) { this.code = c; return this; },
    json(b) { this.body = b; return this; },
    send(b) { this.body = b; return this; },
    end() { return this; },
  };
}

async function post(handler, body) {
  const res = fakeRes();
  await handler({ method: 'POST', headers: { origin: 'https://sidekixhq.com' }, body }, res);
  return res;
}

async function deliver(event) {
  const req = Readable.from([Buffer.from(JSON.stringify(event))]);
  req.method = 'POST';
  req.headers = { 'stripe-signature': 'sig' };
  const res = fakeRes();
  await webhook(req, res);
  return res;
}

function withEnv(flag, fn) {
  return async () => {
    const before = { ...process.env };
    process.env.STRIPE_WEBHOOK_SECRET = 'whsec_test';
    if (flag === undefined) delete process.env.SALES_TAX_ENABLED;
    else process.env.SALES_TAX_ENABLED = flag;
    reset();
    try {
      await fn();
    } finally {
      process.env = before;
    }
  };
}

const succeeded = (metadata, amount) => ({
  type: 'payment_intent.succeeded',
  data: { object: { id: 'pi_test', currency: 'usd', amount_received: amount, metadata } },
});

test('flag off: credits checkout, payment intent and config are unchanged', withEnv(undefined, async () => {
  const s = await post(checkoutSession, { type: 'credits', packs: 2 });
  assert.strictEqual(s.code, 200);
  const params = calls.sessions[0];
  assert.strictEqual(params.automatic_tax, undefined);
  assert.strictEqual(params.billing_address_collection, undefined);
  assert.strictEqual(params.line_items[0].price_data.tax_behavior, undefined);
  assert.strictEqual(params.line_items[0].price_data.unit_amount, 1900);

  const p = await post(paymentIntent, { packs: 2, email: 'a@b.co' });
  assert.strictEqual(p.code, 200);
  assert.strictEqual(calls.calculations.length, 0);
  assert.strictEqual(calls.intents[0].amount, 3800);
  assert.strictEqual(calls.intents[0].metadata.taxCalculationId, undefined);
  assert.deepStrictEqual(calls.intents[0].metadata.credits, '700');

  const c = await post(stripeConfig, {});
  assert.strictEqual(c.body.salesTax, false);
}));

test('flag on: credits Checkout has automatic tax, a required billing address and the product tax code', withEnv('true', async () => {
  const s = await post(checkoutSession, { type: 'credits', packs: 3 });
  assert.strictEqual(s.code, 200);
  const params = calls.sessions[0];
  assert.deepStrictEqual(params.automatic_tax, { enabled: true });
  assert.strictEqual(params.billing_address_collection, 'required');
  const price = params.line_items[0].price_data;
  assert.strictEqual(price.tax_behavior, 'exclusive');
  assert.strictEqual(price.unit_amount, 1900);
  assert.strictEqual(price.product_data.tax_code, 'txcd_10103101');
  assert.strictEqual(params.line_items[0].quantity, 3);
  assert.strictEqual(params.metadata.credits, '1050');
  assert.deepStrictEqual(calls.products, ['prod_V977UwyMv8Wj50']);
}));

test('flag on: an unreadable credits product falls back to the backend credits tax code', withEnv('true', async () => {
  productFails = true;
  await post(checkoutSession, { type: 'credits', packs: 1 });
  assert.strictEqual(calls.sessions[0].line_items[0].price_data.product_data.tax_code, 'txcd_10103000');
}));

test('flag on: membership rate locks are not given automatic tax', withEnv('true', async () => {
  await post(checkoutSession, { type: 'membership', plan: 'core' });
  assert.strictEqual(calls.sessions[0].mode, 'setup');
  assert.strictEqual(calls.sessions[0].automatic_tax, undefined);
}));

test('flag on: embedded payment needs a ZIP code', withEnv('true', async () => {
  const p = await post(paymentIntent, { packs: 1, email: 'a@b.co', postalCode: 'abc' });
  assert.strictEqual(p.code, 400);
  assert.strictEqual(p.body.code, 'postal_code_required');
  assert.strictEqual(calls.intents.length, 0);
}));

test('flag on: embedded payment charges the taxed total and stores the calculation', withEnv('true', async () => {
  const p = await post(paymentIntent, { packs: 2, email: 'a@b.co', postalCode: '27601' });
  assert.strictEqual(p.code, 200);
  const calc = calls.calculations[0];
  assert.deepStrictEqual(calc.customer_details.address, { country: 'US', postal_code: '27601' });
  assert.strictEqual(calc.line_items[0].amount, 3800);
  assert.strictEqual(calc.line_items[0].tax_behavior, 'exclusive');
  assert.strictEqual(calc.line_items[0].tax_code, 'txcd_10103101');
  const intent = calls.intents[0];
  assert.strictEqual(intent.amount, 3800 + 181);
  assert.strictEqual(intent.metadata.taxCalculationId, 'taxcalc_1');
  assert.strictEqual(intent.metadata.subtotalCents, '3800');
  assert.strictEqual(intent.metadata.taxCents, '181');
  assert.strictEqual(intent.metadata.packs, '2');
  assert.strictEqual(intent.metadata.credits, '700');
  assert.deepStrictEqual(p.body, {
    clientSecret: 'pi_test_secret', publishableKey: undefined, amount: 3981, subtotal: 3800, tax: 181, credits: 700,
  });
}));

test('webhook: a taxed embedded payment grants credits by pack and records the tax transaction', withEnv('true', async () => {
  const res = await deliver(succeeded(
    { source: 'website', type: 'credits', packs: '2', credits: '700', email: 'a@b.co', taxCalculationId: 'taxcalc_1', subtotalCents: '3800', taxCents: '181' },
    3981,
  ));
  assert.strictEqual(res.code, 200);
  assert.strictEqual(calls.fetches.length, 1);
  assert.strictEqual(calls.fetches[0].body.credits, 700);
  assert.strictEqual(calls.fetches[0].body.sessionId, 'pi_test');
  assert.strictEqual(calls.transactions.length, 1);
  assert.deepStrictEqual(calls.transactions[0].p, { calculation: 'taxcalc_1', reference: 'pi_test' });
  assert.strictEqual(calls.transactions[0].opts.idempotencyKey, 'sidekix-website-credits-tax-pi_test');
  assert.strictEqual(calls.fetches[0].body.taxTransactionId, 'tax_txn_1');
}));

test('webhook: a tax transaction that already exists for the payment is not an error', withEnv('true', async () => {
  transactionError = Object.assign(new Error('A transaction with reference pi_test already exists'), { type: 'StripeInvalidRequestError' });
  const res = await deliver(succeeded(
    { source: 'website', type: 'credits', packs: '1', credits: '350', email: 'a@b.co', taxCalculationId: 'taxcalc_1' },
    1990,
  ));
  assert.strictEqual(res.code, 200);
  assert.strictEqual(calls.fetches[0].body.credits, 350);
  assert.ok(!('taxTransactionId' in calls.fetches[0].body));
}));

test('webhook: a failed tax transaction asks Stripe to retry', withEnv('true', async () => {
  transactionError = Object.assign(new Error('boom'), { type: 'StripeAPIError' });
  const res = await deliver(succeeded(
    { source: 'website', type: 'credits', packs: '1', credits: '350', email: 'a@b.co', taxCalculationId: 'taxcalc_1' },
    1990,
  ));
  assert.strictEqual(res.code, 502);
  assert.strictEqual(calls.fetches.length, 0);
}));

test('webhook: an untaxed embedded payment creates no tax transaction', withEnv(undefined, async () => {
  const res = await deliver(succeeded(
    { source: 'website', type: 'credits', packs: '1', credits: '350', email: 'a@b.co' },
    1900,
  ));
  assert.strictEqual(res.code, 200);
  assert.strictEqual(calls.fetches[0].body.credits, 350);
  assert.strictEqual(calls.transactions.length, 0);
  assert.ok(!('taxTransactionId' in calls.fetches[0].body));
}));
