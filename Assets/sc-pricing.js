/* ============================================================
   Surf China — site-wide pricing config (private pool buyout)
   SINGLE SOURCE OF TRUTH for the PUBLIC buyout rates on this site.
   Synced from Pricing/calculator.xlsx (SURF-BUYOUT-*-1H-OFF list
   rates) by the update-buyout-promo skill. Change prices there,
   not by hand-editing pages.

   PUBLIC LIST RATES ONLY. This file is served to every visitor at
   /Assets/sc-pricing.js, so it must never carry the negotiated
   buyout discount, its percentage, or any "was / now" pair — a
   competitor or a client can read it straight out of devtools.
   Quote the discount by hand, from the spreadsheet. See CLAUDE.md.

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
    buyout: {              // CNY per 1-hour buyout, off-season public list
      intermediate: { list: 7760 },
      advanced:     { list: 9960 },
      master:       { list: 9960 }
    }
  };
  // <<< SC_PRICING_CONFIG_END

  function fmt(n) { return Math.round(n).toLocaleString('en-US'); }
  function get(path) {
    return path.split('.').reduce(function (o, k) { return o && o[k]; }, window.SC_PRICING);
  }

  function render() {
    var P = window.SC_PRICING;
    // <td data-sc-price="buyout.intermediate.list"></td> → "CNY 7,760"
    Array.prototype.forEach.call(document.querySelectorAll('[data-sc-price]'), function (el) {
      var v = get(el.getAttribute('data-sc-price'));
      if (v != null) el.textContent = 'CNY ' + fmt(v);
    });
    // <span data-sc-num="buyout.advanced.list"></span> → bare "9,960" (no CNY prefix)
    Array.prototype.forEach.call(document.querySelectorAll('[data-sc-num]'), function (el) {
      var v = get(el.getAttribute('data-sc-num'));
      if (v != null) el.textContent = fmt(v);
    });
    // <input data-sc-wave="advanced"> → sets data-promo / data-list for page
    // calculators. Both resolve to the list rate: the calculators still read
    // data-promo as "the price to charge", and a list === promo pair renders no
    // struck-through "was" anchor anywhere.
    Array.prototype.forEach.call(document.querySelectorAll('input[data-sc-wave]'), function (el) {
      var w = P.buyout[el.getAttribute('data-sc-wave')];
      if (!w) return;
      el.setAttribute('data-promo', w.list);
      el.setAttribute('data-list', w.list);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
