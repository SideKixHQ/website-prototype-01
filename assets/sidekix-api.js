(function (w) {
  'use strict';

  var BASES = {
    production: 'https://api.sidekixhq.com',
    staging: 'https://staging-api.sidekixhq.com'
  };
  var PRODUCTION_HOSTS = ['sidekixhq.com', 'www.sidekixhq.com'];

  var host = (w.location.hostname || '').toLowerCase().replace(/\.$/, '');
  var env = PRODUCTION_HOSTS.indexOf(host) !== -1 ? 'production' : 'staging';

  try {
    var param = (new URLSearchParams(w.location.search).get('api') || '').toLowerCase();
    if (Object.prototype.hasOwnProperty.call(BASES, param)) env = param;
  } catch (e) {}

  w.SIDEKIX_API_BASE = w.SIDEKIX_API_BASE || BASES[env];
})(window);
