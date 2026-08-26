/* ============================================================
   Surf China — site-wide pricing config (private pool buyout)
   SINGLE SOURCE OF TRUTH for the buyout promo on this site.
   Synced from Pricing/calculator.xlsx (PROMO_BUYOUT_CLIENT +
   SURF-BUYOUT-*-1H-OFF list rates) by the update-buyout-promo
   skill. Change prices there, not by hand-editing pages.
   NOTE: pages/design-your-buyout.html also carries these CNY
   prices in static HTML (baked <span data-sc-num> fallbacks —
   refreshed at runtime by this file) AND in its JSON-LD Offer/
   FAQPage blocks, which are NOT runtime-refreshed. A price sync
   must update that page's JSON-LD numbers too.
   ============================================================ */
(function () {
  'use strict';

  // >>> SC_PRICING_CONFIG_START (machine-edited — keep format)
  window.SC_PRICING = {
    fx: 7,                 // USD → CNY, client settlement
    buyoutPromoPct: 15,    // client-facing % off every private buyout
    buyout: {              // CNY per 1-hour buyout, off-season public list
      intermediate: { list: 7760, promo: 6600 },
      advanced:     { list: 9960, promo: 8470 },
      master:       { list: 9960, promo: 8470 }
    }
  };
  // <<< SC_PRICING_CONFIG_END

  function fmt(n) { return Math.round(n).toLocaleString('en-US'); }
  function get(path) {
    return path.split('.').reduce(function (o, k) { return o && o[k]; }, window.SC_PRICING);
  }

  function render() {
    var P = window.SC_PRICING;
    // <span data-sc-promopct></span> → the promo percentage number
    Array.prototype.forEach.call(document.querySelectorAll('[data-sc-promopct]'), function (el) {
      el.textContent = P.buyoutPromoPct;
    });
    // <td data-sc-price="buyout.intermediate.list"></td> → "CNY 7,760"
    Array.prototype.forEach.call(document.querySelectorAll('[data-sc-price]'), function (el) {
      var v = get(el.getAttribute('data-sc-price'));
      if (v != null) el.textContent = 'CNY ' + fmt(v);
    });
    // <s data-sc-num="buyout.advanced.list"></s> → bare "9,960" (no CNY prefix)
    Array.prototype.forEach.call(document.querySelectorAll('[data-sc-num]'), function (el) {
      var v = get(el.getAttribute('data-sc-num'));
      if (v != null) el.textContent = fmt(v);
    });
    // <input data-sc-wave="advanced"> → sets data-promo / data-list for page calculators.
    // Add data-sc-listonly where the promo must not be advertised (index.html trip
    // planner): both attributes resolve to the list rate, so the calculator quotes
    // the public price and renders no struck-through "was" anchor.
    Array.prototype.forEach.call(document.querySelectorAll('input[data-sc-wave]'), function (el) {
      var w = P.buyout[el.getAttribute('data-sc-wave')];
      if (!w) return;
      el.setAttribute('data-promo', el.hasAttribute('data-sc-listonly') ? w.list : w.promo);
      el.setAttribute('data-list', w.list);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
