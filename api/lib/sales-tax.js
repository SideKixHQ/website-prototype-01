function isSalesTaxEnabled(env = process.env) {
  return String(env.SALES_TAX_ENABLED ?? '').trim().toLowerCase() === 'true';
}

module.exports = { isSalesTaxEnabled };
