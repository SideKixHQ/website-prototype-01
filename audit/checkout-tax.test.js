const test = require('node:test');
const assert = require('node:assert');
const path = require('path');

const API = path.resolve(__dirname, '..', 'api');
const created = [];

function stub(modulePath, exports) {
  const id = require.resolve(modulePath);
  require.cache[id] = { id, filename: id, loaded: true, exports };
}

function FakeStripe() {
  return {
    checkout: {
      sessions: {
        create: async (params) => {
          created.push(params);
          return { url: 'https://checkout.stripe.test/s' };
        },
      },
    },
  };
}

stub('stripe', FakeStripe);
stub(path.join(API, 'lib', 'live-pricing.js'), {
  getCreditsPricing: async () => ({ standardBundle: { credits: 350, priceUSD: 19 } }),
  getMembershipPlans: async () => ({ core: { name: 'Core', monthlyUsdCents: 9900 } }),
});

const handler = require(path.join(API, 'create-checkout-session.js'));
const { isSalesTaxEnabled } = require(path.join(API, 'lib', 'sales-tax.js'));

async function call(body) {
  created.length = 0;
  const res = {
    code: 0,
    body: null,
    status(c) { this.code = c; return this; },
    json(b) { this.body = b; return this; },
  };
  await handler({ method: 'POST', headers: { origin: 'https://sidekixhq.com' }, body }, res);
  return { res, params: created[0] };
}

function withFlag(value, fn) {
  return async () => {
    const before = process.env.SALES_TAX_ENABLED;
    if (value === undefined) delete process.env.SALES_TAX_ENABLED;
    else process.env.SALES_TAX_ENABLED = value;
    try {
      await fn();
    } finally {
      if (before === undefined) delete process.env.SALES_TAX_ENABLED;
      else process.env.SALES_TAX_ENABLED = before;
    }
  };
}

test('flag reads only an exact true', () => {
  assert.strictEqual(isSalesTaxEnabled({ SALES_TAX_ENABLED: 'true' }), true);
  assert.strictEqual(isSalesTaxEnabled({ SALES_TAX_ENABLED: ' TRUE ' }), true);
  assert.strictEqual(isSalesTaxEnabled({ SALES_TAX_ENABLED: '1' }), false);
  assert.strictEqual(isSalesTaxEnabled({}), false);
});

test('membership rate lock is unchanged with the flag off', withFlag(undefined, async () => {
  const { res, params } = await call({ type: 'membership', plan: 'core' });
  assert.strictEqual(res.code, 200);
  assert.strictEqual(params.mode, 'setup');
  assert.strictEqual(params.billing_address_collection, undefined);
  assert.ok(!params.custom_text.submit.message.includes('sales tax'));
  assert.ok(!params.setup_intent_data.description.includes('sales tax'));
}));

test('membership rate lock collects the billing address and discloses tax with the flag on', withFlag('true', async () => {
  const { res, params } = await call({ type: 'membership', plan: 'core' });
  assert.strictEqual(res.code, 200);
  assert.strictEqual(params.mode, 'setup');
  assert.strictEqual(params.billing_address_collection, 'required');
  assert.strictEqual(params.automatic_tax, undefined);
  assert.match(params.custom_text.submit.message, /\$99 a month plus applicable sales tax, your locked rate/);
  assert.match(params.setup_intent_data.description, /\$99 a month plus applicable sales tax/);
  assert.strictEqual(params.metadata.lockedMonthlyUsdCents, '9900');
}));

test('credits checkout gets none of the rate-lock tax copy', withFlag('true', async () => {
  const { res, params } = await call({ type: 'credits', packs: 2 });
  assert.strictEqual(res.code, 200);
  assert.strictEqual(params.mode, 'payment');
  assert.strictEqual(params.setup_intent_data, undefined);
  assert.ok(!params.custom_text.submit.message.includes('sales tax'));
}));
