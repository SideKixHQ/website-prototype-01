/* SideKix anonymous quiz and discovery telemetry.
 *
 * What this sends: which quiz, which answers, which result, how long it took,
 * and a coarse viewport bucket. What it does not send, and cannot: names,
 * emails, IP-derived identity, cookies, or anything that survives the tab
 * closing. The session id lives in sessionStorage, so it is gone when the tab
 * is gone. Its only job is joining a "start" row to its "complete" row so the
 * panel can compute a drop-off rate. Nothing here follows a person between
 * two visits, which is what keeps this outside consent-banner territory.
 *
 * TO SWITCH ON: set ENDPOINT below to the panel's collector URL. Every quiz
 * and the Energy Discovery already load this file, so one edit here turns
 * collection on across the whole site with no page rebuild.
 */
(function (w, d) {
  'use strict';

  var ENDPOINT = '';           /* e.g. 'https://panel.sidekixhq.com/api/collect' */
  var DEBUG_KEY = 'kx_tap';    /* ?kx_tap=1 logs events to the console instead */

  /* Do Not Track and Global Privacy Control are honoured before anything else
     runs, so an opted-out visitor generates no events at all rather than
     events we drop later. */
  if (w.doNotTrack === '1' || navigator.doNotTrack === '1' || navigator.globalPrivacyControl) {
    w.kx = { ev: function () {} };
    return;
  }

  var tap = false;
  try { tap = new URLSearchParams(w.location.search).has(DEBUG_KEY); } catch (e) {}

  function sid() {
    try {
      var k = 'kx_sid', v = sessionStorage.getItem(k);
      if (!v) {
        v = (Date.now().toString(36) + Math.random().toString(36).slice(2, 10));
        sessionStorage.setItem(k, v);
      }
      return v;
    } catch (e) { return 'nostore'; }
  }

  /* Width as a bucket, not a number. A raw viewport size is a weak
     fingerprinting signal and the panel only ever wants the three buckets. */
  function bucket() {
    var x = w.innerWidth || 0;
    return x < 700 ? 'm' : (x < 1100 ? 't' : 'd');
  }

  /* Referrer host only. The full referring URL can carry query strings from
     someone else's site, which is not ours to collect. */
  function refHost() {
    try { return d.referrer ? new URL(d.referrer).hostname : ''; } catch (e) { return ''; }
  }

  var t0 = Date.now();
  var queue = [];

  function flush() {
    if (!queue.length) return;
    var body = JSON.stringify({ v: 1, events: queue.splice(0, queue.length) });
    if (tap) { try { console.log('[kx]', JSON.parse(body)); } catch (e) {} return; }
    if (!ENDPOINT) return;
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, new Blob([body], { type: 'application/json' }));
      } else {
        fetch(ENDPOINT, { method: 'POST', body: body, keepalive: true,
                          headers: { 'Content-Type': 'application/json' } });
      }
    } catch (e) {}
  }

  /* Events batch until the page is being put away, so a completed quiz costs
     one request rather than eight. pagehide is the one that fires reliably on
     mobile Safari, where unload does not. */
  function ev(kind, props) {
    var e = { k: kind, sid: sid(), ts: Date.now(), el: Date.now() - t0,
              w: bucket(), ref: refHost(), path: d.location.pathname };
    var src = props || {};
    for (var p in src) if (Object.prototype.hasOwnProperty.call(src, p)) e[p] = src[p];
    queue.push(e);
    if (tap) flush();
    /* A completion is the row that matters most, so it does not wait. */
    if (kind === 'complete') flush();
  }

  d.addEventListener('visibilitychange', function () {
    if (d.visibilityState === 'hidden') flush();
  });
  w.addEventListener('pagehide', flush);

  w.kx = { ev: ev, flush: flush };
})(window, document);
