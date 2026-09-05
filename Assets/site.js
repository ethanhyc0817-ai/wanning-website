function scrollWpGallery(dir) {
  const el = document.getElementById('wp-gallery-grid');
  if (!el) return;
  const item = el.querySelector('.gallery-item');
  const gap = 12; // matches CSS gap: 0.75rem
  const amt = (item ? item.offsetWidth : 320) + gap;
  el.scrollBy({ left: amt * dir, behavior: 'smooth' });
}

// Swap a single video's data-src -> src and start buffering. Play is separate:
// preloading happens well before the viewport, playback only near it.
function loadVideo(vid) {
  if (vid.dataset.poster) {
    vid.poster = vid.dataset.poster;
    delete vid.dataset.poster;
  }
  let swapped = false;
  vid.querySelectorAll('source[data-src]').forEach(s => {
    s.src = s.dataset.src;
    s.removeAttribute('data-src');
    swapped = true;
  });
  if (!swapped) return;
  // The markup ships preload="none" so nothing streams on page load; once we
  // decide to preload, let the browser actually buffer ahead.
  vid.preload = 'auto';
  try { vid.load(); } catch (e) {}
}

function playVideo(vid) {
  loadVideo(vid); // no-op if already swapped
  if (vid.hasAttribute('autoplay') && vid.paused) {
    const p = vid.play();
    if (p && typeof p.catch === 'function') { p.catch(() => {}); }
  }
}

// Two tiers. Preload: ~two viewports ahead, the poster and the stream start
// downloading silently, so by the time the visitor scrolls there the frame is
// already painted — no blank box on a fast fling. Play: near the viewport the
// clip starts, and it pauses again once it scrolls well away.
const videoPreloadObserver = ('IntersectionObserver' in window)
  ? new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadVideo(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { rootMargin: '2000px 0px' })
  : null;

const lazyVideoObserver = ('IntersectionObserver' in window)
  ? new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const vid = entry.target;
        if (entry.isIntersecting) {
          playVideo(vid);
        } else if (!vid.paused) {
          try { vid.pause(); } catch (e) {}
        }
      });
    }, { rootMargin: '300px 0px' })
  : null;

function observeLazyVideos(scope) {
  (scope || document).querySelectorAll('video').forEach(vid => {
    if (vid.dataset.lazyObserved) return;
    vid.dataset.lazyObserved = '1';
    // No IntersectionObserver support (very old browsers): just load it.
    if (!lazyVideoObserver) { playVideo(vid); return; }
    videoPreloadObserver.observe(vid);
    lazyVideoObserver.observe(vid);
  });
}

function activateLazyMedia(scope) {
  if (!scope) return;
  // Swap data-src -> src on iframes inside the activated page
  scope.querySelectorAll('iframe[data-src]').forEach(ifr => {
    ifr.src = ifr.dataset.src;
    ifr.removeAttribute('data-src');
  });
  // Videos go through the viewport observer rather than loading all at once.
  // Hidden pages are display:none, so nothing in them can intersect until shown.
  observeLazyVideos(scope);
}
function showPage(page, fromPopState) {
  // When called from inline onclick on <a href="#" onclick="showPage(...)">, prevent
  // the default href="#" navigation so we don't leave stray "#" history entries.
  try {
    if (window.event && typeof window.event.preventDefault === 'function') {
      window.event.preventDefault();
    }
  } catch (e) { /* noop */ }

  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  if (page !== 'contact') { const bb = document.getElementById('bywBar'); if (bb) bb.hidden = true; }
  const target = document.getElementById('page-' + page);
  if (target) {
    target.classList.add('active');
    activateLazyMedia(target);
  }
  document.querySelectorAll('.nav-links a[data-page]').forEach(a => {
    a.classList.toggle('active', a.dataset.page === page);
  });

  if (!fromPopState) {
    // Forward navigation triggered by a user click — sync browser history so the
    // back button returns to the previous internal page (and to the homepage scroll
    // position the user came from), not a stale detail section.
    const newHash = (page === 'home') ? '' : '#' + page;
    const currentHash = window.location.hash || '';
    if (currentHash !== newHash) {
      const newUrl = window.location.pathname + window.location.search + newHash;
      try { window.history.pushState({ page: page }, '', newUrl); } catch (e) { /* noop */ }
    }
    // Show the new page from the top.
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  // When fromPopState is true (browser Back/Forward), do NOT force-scroll —
  // let the browser naturally restore the previous scroll position.

  // Re-trigger fade-in animations
  setTimeout(() => {
    document.querySelectorAll('.page.active .fade-in:not(.visible)').forEach(el => observer.observe(el));
  }, 100);

  // GA4: log SPA section views as distinct page_views (so #contact / #wavepool /
  // #packages show up individually). Skip the very first render — GA's default
  // pageview already covers the landing — to avoid double-counting.
  try {
    if (window.__spaNavStarted && typeof gtag === 'function') {
      gtag('event', 'page_view', {
        page_title: document.title + ' — ' + page,
        page_location: window.location.href,
        page_path: window.location.pathname + window.location.search + (page === 'home' ? '' : '#' + page)
      });
    }
    window.__spaNavStarted = true;
  } catch (e) { /* analytics is best-effort */ }
  return false;
}

// Browser Back/Forward — restore the prior internal page from history state.
// Pass fromPopState=true so we don't push a duplicate history entry and don't
// force-scroll (so the browser's natural scroll restoration can run).
window.addEventListener('popstate', function (e) {
  const fromState = e && e.state && e.state.page;
  const fromHash = (window.location.hash || '').replace('#', '').trim();
  const page = fromState || fromHash || 'home';
  if (document.getElementById('page-' + page)) {
    showPage(page, true);
  } else {
    showPage('home', true);
  }
  // Booking steps live in this history too: tell the frame which step this entry is.
  if (page === 'contact') {
    var fr = document.getElementById('bywFrame');
    var n = (e && e.state && typeof e.state.byw === 'number') ? e.state.byw : 0;
    if (fr && fr.contentWindow) { try { fr.contentWindow.postMessage({ byw: 'goto', n: n }, window.location.origin); } catch (err) {} }
  }
});
window.addEventListener('scroll', () => {
  document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 80);
});
function toggleMobile() {
  document.getElementById('mobileMenu').classList.toggle('open');
}
document.addEventListener('click', (e) => {
  const faqItem = e.target.closest('.faq-item');
  if (faqItem) faqItem.classList.toggle('open');
});
const observer = new IntersectionObserver((entries) => {
  // Elements that enter the viewport in the same batch reveal with a small
  // stagger (60ms steps, capped) instead of popping in all at once.
  const entering = entries.filter(e => e.isIntersecting);
  entering.forEach((entry, i) => {
    entry.target.style.setProperty('--stagger', (Math.min(i, 5) * 60) + 'ms');
    entry.target.classList.add('visible');
    observer.unobserve(entry.target); // reveal fires once; re-animating on every scroll-by fights the reader
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
// Section headings and card groups site-wide get the reveal too, not just the
// elements hand-tagged in the markup. Applied from JS so a no-JS visitor (and
// search crawlers) never see opacity:0 content. Hero is excluded — it has its
// own entrance — and anything nested inside an already-tagged element is skipped.
document.querySelectorAll('.page section h2, .page section .overline, .page section .lead, .intro-card, .reassurance-pillar').forEach(el => {
  if (el.closest('.hero')) return;
  const tagged = el.parentElement && el.parentElement.closest('.fade-in');
  if (tagged) return;
  el.classList.add('fade-in');
});
document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
// Register the landing page's videos with the viewport observer. Later pages get
// registered by activateLazyMedia() when showPage() reveals them.
observeLazyVideos(document.querySelector('.page.active') || document);
const pageObserver = new MutationObserver(() => {
  document.querySelectorAll('.fade-in:not(.visible)').forEach(el => observer.observe(el));
});
document.querySelectorAll('.page').forEach(page => {
  pageObserver.observe(page, { attributes: true, attributeFilter: ['class'] });
});
// Trip Start Date: a single readonly field opens a calendar popover for picking
// the trip start date. "I'm not sure yet" toggle lives inside the popover.
// Hidden inputs trip_start_date / dates_tbd hold the values for submit.
(function initDatePicker() {
  const display = document.getElementById('dateDisplay');
  const popover = document.getElementById('datePopover');
  const startInput = document.getElementById('tripStartDate');
  const tbdInput = document.getElementById('datesTbd');
  if (!display || !popover) return;

  const today = new Date(); today.setHours(0, 0, 0, 0);
  // Booking horizon: up to 2 years from today. Rolls forward automatically each day.
  const MAX_DATE = new Date(today.getFullYear() + 2, today.getMonth(), today.getDate());
  MAX_DATE.setHours(0, 0, 0, 0);
  // Surf pool maintenance closures: start dates in these windows can't be
  // picked, and a note shows under the field until each window has passed.
  // Add future closures here as they're announced (month is 0-based).
  const MAINT_RANGES = [
    { start: new Date(2026, 7, 24), end: new Date(2026, 8, 23) } // 24 Aug – 23 Sep 2026
  ];
  MAINT_RANGES.forEach(r => { r.start.setHours(0,0,0,0); r.end.setHours(0,0,0,0); });
  const inMaintenance = d => MAINT_RANGES.some(r => d >= r.start && d <= r.end);
  const maintNote = document.getElementById('maintNote');
  if (maintNote) {
    const upcoming = MAINT_RANGES.filter(r => today <= r.end);
    if (upcoming.length) {
      const fmtNote = d => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      maintNote.innerHTML = 'Our surf pool is closed for scheduled maintenance '
        + upcoming.map(r => '<strong>' + fmtNote(r.start) + ' &ndash; ' + fmtNote(r.end) + '</strong>').join(' and ')
        + ', so trips can&rsquo;t start on those dates.';
      maintNote.hidden = false;
    }
  }
  // National Day Golden Week (Oct 1-7, every year): still bookable, but stays
  // over these dates carry a 20% holiday surcharge — we mark the days gold and
  // nudge visitors to book around them. One range per year in the horizon.
  const HOLIDAY_RANGES = [];
  for (let yr = today.getFullYear(); yr <= MAX_DATE.getFullYear(); yr++) {
    HOLIDAY_RANGES.push({ start: new Date(yr, 9, 1), end: new Date(yr, 9, 7) });
  }
  HOLIDAY_RANGES.forEach(r => { r.start.setHours(0,0,0,0); r.end.setHours(0,0,0,0); });
  const inHoliday = d => HOLIDAY_RANGES.some(r => d >= r.start && d <= r.end);
  const holidayNote = document.getElementById('holidayNote');
  const HOLIDAY_PICKED = 'Your start date falls in <strong>Golden Week (Oct 1&ndash;7)</strong>, so a <strong>20% holiday surcharge</strong> applies. Start <strong>Oct 8 or later</strong> for standard rates.';
  // The note only appears once a Golden Week start date is actually picked —
  // before that, the red calendar marking and legend do the nudging.
  function refreshHolidayNote() {
    if (!holidayNote) return;
    if (selectedDate && inHoliday(selectedDate)) {
      holidayNote.innerHTML = HOLIDAY_PICKED;
      holidayNote.classList.add('picked');
      holidayNote.hidden = false;
    } else {
      holidayNote.hidden = true;
    }
  }
  let viewDate = new Date(today.getFullYear(), today.getMonth(), 1);
  let selectedDate = null;
  let isTbd = false;
  let allowTbd = true;
  refreshHolidayNote();

  const TBD_TEXT = "Dates TBD — we'll figure them out together";

  // Programmatic value changes on hidden inputs don't fire native change
  // events. We dispatch one ourselves so form-level validators can react.
  function notify() {
    refreshHolidayNote();
    startInput.dispatchEvent(new Event('change', { bubbles: true }));
  }

  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const DOW = ['S','M','T','W','T','F','S'];

  const fmtIso = d => d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
  const fmtShort = d => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const sameDay = (a, b) => a && b && fmtIso(a) === fmtIso(b);

  function render() {
    const y = viewDate.getFullYear();
    const m = viewDate.getMonth();
    const firstDay = new Date(y, m, 1);
    const daysInMonth = new Date(y, m + 1, 0).getDate();
    const startOffset = firstDay.getDay();

    let html = '';
    // Disable prev-month / prev-year nav when going back would land entirely in the past.
    const lastDayPrevMonth = new Date(y, m, 0); lastDayPrevMonth.setHours(0,0,0,0);
    const lastDayPrevYearSameMonth = new Date(y - 1, m + 1, 0); lastDayPrevYearSameMonth.setHours(0,0,0,0);
    const disablePrevMonth = lastDayPrevMonth < today;
    const disablePrevYear = lastDayPrevYearSameMonth < today;
    // Disable next-month / next-year nav when going forward would cross the MAX_DATE cap.
    const firstDayNextMonth = new Date(y, m + 1, 1); firstDayNextMonth.setHours(0,0,0,0);
    const firstDayNextYearSameMonth = new Date(y + 1, m, 1); firstDayNextYearSameMonth.setHours(0,0,0,0);
    const disableNextMonth = firstDayNextMonth > MAX_DATE;
    const disableNextYear = firstDayNextYearSameMonth > MAX_DATE;

    html += '<div class="date-popover-header">';
    html += '<div class="date-popover-nav-group">';
    html += '<button type="button" class="date-popover-nav" data-act="prev" aria-label="Previous month" title="Previous month"' + (disablePrevMonth ? ' disabled' : '') + '>&lsaquo;</button>';
    html += '</div>';
    html += '<div class="date-popover-title">' + MONTHS[m] + ' ' + y + '</div>';
    html += '<div class="date-popover-nav-group">';
    html += '<button type="button" class="date-popover-nav" data-act="next" aria-label="Next month" title="Next month"' + (disableNextMonth ? ' disabled' : '') + '>&rsaquo;</button>';
    html += '</div>';
    html += '</div>';
    // "I'm not sure yet" row — at the top, right below the header. A deliberate
    // choice the visitor must tick; it still counts as answering the (required) date.
    if (allowTbd) {
      html += '<div class="date-popover-tbd' + (isTbd ? ' active' : '') + '" data-act="tbd">';
      html += '<span class="tbd-check" aria-hidden="true"></span>';
      html += '<span>I&rsquo;m not sure yet</span>';
      html += '</div>';
    }
    html += '<div class="date-cal">';
    DOW.forEach(d => html += '<div class="date-cal-dow">' + d + '</div>');
    for (let i = 0; i < startOffset; i++) html += '<div></div>';
    let monthHasHoliday = false;
    for (let day = 1; day <= daysInMonth; day++) {
      const cell = new Date(y, m, day); cell.setHours(0, 0, 0, 0);
      let cls = 'date-cal-day';
      if (cell < today || cell > MAX_DATE) cls += ' disabled';
      const maint = inMaintenance(cell);
      if (maint) cls += ' disabled maint';
      const holiday = !maint && inHoliday(cell);
      if (holiday) { cls += ' holiday'; monthHasHoliday = true; }
      if (sameDay(cell, selectedDate)) cls += ' start';
      const title = maint ? 'Closed for surf pool maintenance'
        : (holiday ? 'National Day Golden Week — 20% holiday surcharge' : '');
      html += '<div class="' + cls + '" data-day="' + day + '"' + (title ? ' title="' + title + '"' : '') + '>' + day + '</div>';
    }
    html += '</div>';
    if (monthHasHoliday) {
      html += '<div class="date-holiday-legend"><span class="swatch" aria-hidden="true"></span><span>Oct 1&ndash;7 &middot; Golden Week &middot; 20% holiday surcharge</span></div>';
    }
    html += '<div class="date-popover-footer">';
    html += '<button type="button" class="btn-clear" data-act="clear">Clear</button>';
    html += '</div>';
    popover.innerHTML = html;

    popover.querySelectorAll('[data-act]').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const act = btn.dataset.act;
        if (act === 'prev') { viewDate.setMonth(viewDate.getMonth() - 1); render(); }
        else if (act === 'next') { viewDate.setMonth(viewDate.getMonth() + 1); render(); }
        else if (act === 'clear') {
          selectedDate = null;
          isTbd = false;
          startInput.value = ''; tbdInput.value = '';
          display.value = ''; display.classList.remove('tbd');
          render();
          notify();
        } else if (act === 'tbd') {
          if (isTbd) {
            // Toggle OFF — back to pickable empty state
            isTbd = false;
            tbdInput.value = '';
            display.value = ''; display.classList.remove('tbd');
            render();
          } else {
            // Toggle ON — clear any picked date, mark TBD, close
            selectedDate = null;
            isTbd = true;
            startInput.value = ''; tbdInput.value = 'yes';
            display.value = TBD_TEXT; display.classList.add('tbd');
            closePopover();
          }
          notify();
        }
      });
    });
    popover.querySelectorAll('.date-cal-day:not(.disabled)').forEach(cell => {
      const day = parseInt(cell.dataset.day, 10);
      const d = new Date(y, m, day); d.setHours(0, 0, 0, 0);
      cell.addEventListener('click', e => {
        e.stopPropagation();
        // Picking a date always clears the TBD flag
        if (isTbd) { isTbd = false; tbdInput.value = ''; display.classList.remove('tbd'); }
        selectedDate = d;
        startInput.value = fmtIso(d);
        updateDisplay();
        closePopover();
        notify();
      });
    });
  }

  function updateDisplay() {
    if (!selectedDate) { display.value = ''; return; }
    display.value = selectedDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function openPopover() {
    popover.classList.add('open');
    display.classList.add('open');
    render();
  }
  function closePopover() {
    popover.classList.remove('open');
    display.classList.remove('open');
  }

  display.addEventListener('click', e => {
    e.stopPropagation();
    if (popover.classList.contains('open')) closePopover();
    else openPopover();
  });
  document.addEventListener('click', e => {
    if (!popover.contains(e.target) && e.target !== display) closePopover();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && popover.classList.contains('open')) closePopover();
  });

  window.scDatePicker = {
    setAllowTbd: function (on) {
      allowTbd = !!on;
      if (!allowTbd && isTbd) {
        isTbd = false; tbdInput.value = '';
        display.value = ''; display.classList.remove('tbd');
        notify();
      }
      if (popover.classList.contains('open')) render();
    }
  };
})();

// Inquiry form validation: runs on submit, lists what's missing in a red
// block above the button, and red-highlights the offending fields.
// As soon as the user edits a flagged field, its red highlight clears.
function validateInquiryForm(form) {
  const missing = [];        // human-readable list shown to the user
  const errorFields = [];    // DOM elements to add .has-error to

  const fullName = form.querySelector('[name="full_name"]');
  const email = form.querySelector('[name="email"]');
  const checkboxes = form.querySelectorAll('input[name="interested_in"]');
  const tripStart = form.querySelector('#tripStartDate');
  const tbd = form.querySelector('#datesTbd');

  if (!fullName || !fullName.value.trim()) {
    missing.push('Your name');
    if (fullName) errorFields.push(fullName.closest('.form-group'));
  }
  if (!email || !email.value.trim()) {
    missing.push('Email');
    if (email) errorFields.push(email.closest('.form-group'));
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
    missing.push('A valid email address');
    errorFields.push(email.closest('.form-group'));
  }
  const anyPackage = Array.from(checkboxes).some(cb => cb.checked);
  if (!anyPackage) {
    missing.push('Which package you’re interested in');
    errorFields.push(form.querySelector('.pkg-section:not([hidden]) .package-options') || form.querySelector('.pkg-tabs') || form.querySelector('.package-options'));
  }
  // Custom trip must declare a focus (surf / golf / both) so we have a base to plan from.
  const customBox = form.querySelector('input[data-custom="1"]');
  if (customBox && customBox.checked && !form.querySelector('input[name="custom_focus"]:checked')) {
    missing.push('Your custom trip focus (surf, golf, or both)');
    errorFields.push(document.getElementById('customDetail'));
  }
  if (customBox && customBox.checked && !form.querySelector('input[name="custom_budget"]:checked')) {
    missing.push('A budget level for your custom trip');
    errorFields.push(document.getElementById('customDetail'));
  }
  if (customBox && customBox.checked) {
    const cn = document.getElementById('customNights');
    if (!cn || !(Number(cn.value) >= 1)) {
      missing.push('Number of nights for your custom trip');
      errorFields.push(document.getElementById('customDetail'));
    }
  }
  // Date rules follow the trip type: Surf Escape pricing is date-based, so a
  // real date is required there; Surf & Golf and Custom quotes can start without one.
  const seBox = form.querySelector('input[data-package-key="wave-pool"]');
  if (seBox && seBox.checked && !(tripStart && tripStart.value)) {
    missing.push('Your trip start date — Surf Escape pricing is date-based');
    errorFields.push(document.getElementById('datePicker'));
  }
  const adults = form.querySelector('[name="adults"]');
  if (adults) {
    if (!adults.value.trim() || !(Number(adults.value) >= 1)) {
      missing.push('Number of adults');
      errorFields.push(adults.closest('.form-group'));
    }
  }
  const rooms = form.querySelector('[name="rooms"]');
  if (rooms) {
    if (!rooms.value.trim() || !(Number(rooms.value) >= 1)) {
      missing.push('Number of rooms');
      errorFields.push(rooms.closest('.form-group'));
    }
  }
  return { missing, errorFields };
}

// Package selector: enforce "only one at a time". When the user ticks a
// new card, auto-untick any other. Click the same card again to clear.
(function initSinglePackageSelect() {
  const boxes = document.querySelectorAll('input[name="interested_in"]');
  if (!boxes.length) return;
  // Each package implies its length, so Nights re-fills to the selected package's
  // length on every switch (still editable within Surf Pool, e.g. 3 vs 4).
  const nights = document.querySelector('#contactForm [name="num_nights"]');
  // Reveal the custom-detail block only when the Custom option is selected.
  const customBox = document.querySelector('#contactForm input[data-custom="1"]');
  const customDetail = document.getElementById('customDetail');
  function syncCustom() {
    const on = !!(customBox && customBox.checked);
    if (customDetail) customDetail.hidden = !on;
    // Only one num_nights submits: Custom's when Custom is selected, the Surf Pool / package one otherwise.
    const cn = document.getElementById('customNights'); if (cn) cn.disabled = !on;
    const wn = document.getElementById('wpeNights'); if (wn) wn.disabled = on;
  }
  const wpeBox = document.querySelector('#contactForm input[data-package-key="wave-pool"]');
  const wpeEst = document.getElementById('wpeEstimate');
  // Live The Surf Escape estimate — reads the shared group/date fields (asked once above),
  // adds only its own Surf sessions. Current package model (calculator, 2026-08-14 Garden View):
  // FX 7, coordination per room 3N $282 / 4N $391, scaled by rooms.
  const FX = 7, usd = n => '$' + Math.round(n).toLocaleString();
  const coordPerRoom = (n, solo) => solo
      ? (n === 4 ? 388 : n === 3 ? 279 : 93 * n)   // solo room
      : (n === 4 ? 391 : n === 3 ? 282 : 94 * n);  // shared room
  const g = id => document.getElementById(id);
  const fld = name => document.querySelector('#contactForm [name="' + name + '"]');
  const numVal = (el, d) => { const v = parseFloat((el && el.value) || ''); return isNaN(v) ? d : v; };
  // Surf sessions are entered as a per-day cadence (default 2/day, whole group); total = nights × per-day.
  function readPeople() { const a = Math.max(0, Math.round(numVal(fld('adults'), 0))); const c = Math.max(0, Math.round(numVal(fld('children'), 0))); const p = a + c; return p > 0 ? p : 2; }
  function readNights() { return Math.max(1, Math.round(numVal(fld('num_nights'), 3))); }
  function readRooms(people) { const r = Math.round(numVal(fld('rooms'), 0)); return r > 0 ? r : Math.ceil(people / 2); }
  function readPerDay() { return Math.max(0, Math.round(numVal(g('wpeSessionsPerDay'), 2))); }
  function calcWpe() {
    if (!wpeEst) return;
    const ppl = readPeople(), nts = readNights(), rooms = readRooms(ppl);
    const ses = nts * readPerDay();  // total group sessions = nights × sessions/day
    // Private pool: public list rate per hour from Assets/sc-pricing.js, priced per hour, not per head.
    const base = rooms*nts*(850*1.15/FX) + ses*(500*1.10/FX) + rooms*(900*1.80/FX) + ppl*(200*2/FX) + rooms*coordPerRoom(nts, ppl === 1);
    const addons = (typeof window.scAddonsRmb === 'function') ? window.scAddonsRmb() : { promo: 0, list: 0, label: '' };
    const total = base + addons.promo/FX;
    // The buyout anchors against its own list rate (sc-pricing.js), not the package uplift.
    const listTotal = base*1.1 + addons.list/FX;
    g('wpePP').textContent = usd(total / ppl);
    g('wpeTot').textContent = usd(total) + ' total';
    g('wpeList').textContent = 'was ' + usd(listTotal);
    g('wpeBasis').textContent = ppl + ' guest' + (ppl > 1 ? 's' : '');
    const q = g('wpeQuoted'); if (q) q.value = usd(total) + ' total · ' + usd(total / ppl) + ' pp · ' + nts + 'N × ' + readPerDay() + ' sessions/day' + (addons.label ? ' + ' + addons.label : '');
  }
  function wpeRefresh() { calcWpe(); }
  window.scRefreshEstimate = wpeRefresh;
  function syncWpe() {
    if (!wpeEst) return;
    wpeEst.hidden = !(wpeBox && wpeBox.checked);
    const sp = g('wpeSessionsPerDay'); if (sp) sp.disabled = wpeEst.hidden;
    const qh = g('wpeQuoted'); if (qh) qh.disabled = wpeEst.hidden;  // only submit sessions/day when Surf Pool is selected
    if (!wpeEst.hidden) wpeRefresh();
  }
  if (wpeEst) {
    g('wpeSessionsPerDay').addEventListener('input', calcWpe);
    ['adults', 'children', 'rooms', 'num_nights'].forEach(name => { const el = fld(name); if (el) el.addEventListener('input', wpeRefresh); });
  }
  // Rooms follows Adults (1 room per 2 adults) until the visitor sets it themselves.
  const adultsFld = fld('adults'), roomsFld = fld('rooms');
  let roomsManual = false;
  if (roomsFld) roomsFld.addEventListener('input', () => { roomsManual = roomsFld.value.trim() !== ''; });
  if (adultsFld && roomsFld) adultsFld.addEventListener('input', () => {
    if (!roomsManual) roomsFld.value = Math.max(1, Math.ceil((parseFloat(adultsFld.value) || 1) / 2));
    if (typeof wpeRefresh === 'function') wpeRefresh();
  });
  // Ask for children's ages only when there's at least one child (beds, min surf age, infant gear).
  const childrenFld = fld('children'), agesGroup = g('childrenAgesGroup'), agesInput = g('childrenAges');
  function syncAges() {
    if (!agesGroup) return;
    const show = Math.round(numVal(childrenFld, 0)) > 0;
    agesGroup.hidden = !show;
    if (agesInput) { agesInput.disabled = !show; if (!show) agesInput.value = ''; }
  }
  if (childrenFld) childrenFld.addEventListener('input', syncAges);
  syncAges();
  boxes.forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked) {
        boxes.forEach(other => {
          if (other !== cb && other.checked) other.checked = false;
        });
        if (nights && cb.dataset.nights) nights.value = cb.dataset.nights;
      }
      syncCustom();
      syncWpe();
    });
  });
  syncCustom();
  syncWpe();
})();

// Custom Trip: reveal the surf-sessions / golf-rounds sub-questions only when the
// matching focus is ticked; clear + disable them when hidden so they never submit stray values.
(function initCustomFocusDetail() {
  const form = document.getElementById('contactForm');
  if (!form) return;
  const focusBoxes = form.querySelectorAll('input[name="custom_focus"]');
  if (!focusBoxes.length) return;
  const checked = v => Array.from(focusBoxes).some(b => b.checked && b.value === v);
  function toggle(on, qId, inputId) {
    const q = document.getElementById(qId), inp = document.getElementById(inputId);
    if (q) q.hidden = !on;
    if (inp) { inp.disabled = !on; if (!on) inp.value = ''; }
  }
  // Live headcount hint next to "How many surf sessions" — pulls the group size
  // the visitor already entered above, so they calibrate the total correctly.
  const paxEl = document.getElementById('customSurfPax');
  const golfPaxEl = document.getElementById('customGolfPax');
  const adultsFld = form.querySelector('[name="adults"]'), childrenFld = form.querySelector('[name="children"]');
  function updatePax() {
    const a = Math.max(0, parseInt((adultsFld && adultsFld.value) || '0', 10) || 0);
    const c = Math.max(0, parseInt((childrenFld && childrenFld.value) || '0', 10) || 0);
    if (paxEl) {  // surf: adults + children (kids surf too)
      let s = a ? (a + ' adult' + (a > 1 ? 's' : '')) : '';
      if (c) s += (s ? ' + ' : '') + c + (c > 1 ? ' children' : ' child');
      paxEl.textContent = s ? (' · ' + s) : '';
    }
    if (golfPaxEl) {  // golf: adults only (golfers)
      golfPaxEl.textContent = a ? (' · ' + a + ' adult' + (a > 1 ? 's' : '')) : '';
    }
  }
  function sync() {
    toggle(checked('Surf'), 'customSurfQ', 'customSurfSessions');
    toggle(checked('Golf'), 'customGolfQ', 'customGolfRounds');
    updatePax();
    // Surf-only custom trips drop the golfers field, same as the Surf tab.
    if (typeof syncTripModeFields === 'function') syncTripModeFields();
  }
  focusBoxes.forEach(b => b.addEventListener('change', sync));
  if (adultsFld) adultsFld.addEventListener('input', updatePax);
  if (childrenFld) childrenFld.addEventListener('input', updatePax);
  sync();
})();

// Package picker tabs — show one section (Surf / Surf & Golf / Custom) at a time.
(function initPkgTabs() {
  const tabs = document.querySelectorAll('#contactForm .pkg-tab');
  const secs = document.querySelectorAll('#contactForm .pkg-section');
  if (!tabs.length) return;
  function show(sec) {
    tabs.forEach(t => t.classList.toggle('active', t.dataset.section === sec));
    secs.forEach(s => { s.hidden = (s.dataset.section !== sec); });
    const active = Array.from(secs).find(s => s.dataset.section === sec);
    if (!active) return;
    const opts = active.querySelectorAll('input[name="interested_in"]');
    if (opts.length === 1) {
      // Single-option tabs (Surf, Custom): auto-select it for the visitor.
      if (!opts[0].checked) { opts[0].checked = true; opts[0].dispatchEvent(new Event('change', { bubbles: true })); }
    } else {
      // Multi-option tab (Surf & Golf): clear any selection carried in from
      // another tab so the visitor picks a tier; keep a tier already chosen here.
      document.querySelectorAll('#contactForm input[name="interested_in"]:checked').forEach(cb => {
        if (!active.contains(cb)) { cb.checked = false; cb.dispatchEvent(new Event('change', { bubbles: true })); }
      });
    }
  }
  tabs.forEach(t => t.addEventListener('click', () => show(t.dataset.section)));
})();

// Trip-type modes: Step 1 picks the path, the rest of the form adapts.
// surf = The Surf Escape (fixed calculator pricing -> date required, no TBD,
// estimate is the offer). surf-golf / custom = tailored quotes (date optional,
// TBD allowed with a rough-timing follow-up).
var currentTripMode = '';
// "Tell Us More" and "Number of Golfers" only earn their place on the paths where
// golf is in play or the trip is being built from scratch. On the Surf path the
// package is fixed and the form already asks surf level, sessions/day, dates and
// kids' ages — so the open-ended box is dropped rather than left to collect noise.
// A hoisted function, not a var — the custom-focus block below calls into this
// one before the trip-mode statements have run.
function messagePlaceholderFor(mode) {
  if (mode === 'surf-golf') return 'Tell us about your ideal trip — who’s coming, golf handicap, must-dos, special occasions, anything that matters to you. The more you share, the more precisely we can tailor the plan around you.';
  if (mode === 'custom') return 'Tell us what this trip is built around — what you want more of, must-dos, special occasions, anything that matters to you. The more you share, the more precisely we can shape it.';
  if (mode === 'surf') return 'Anything we should know?';
  return '';
}
function customFocusIsSurfOnly() {
  var boxes = document.querySelectorAll('#contactForm input[name="custom_focus"]');
  if (!boxes.length) return false;
  var surf = false, golf = false;
  boxes.forEach(function (b) {
    if (!b.checked) return;
    if (b.value === 'Surf') surf = true;
    if (b.value === 'Golf') golf = true;
  });
  return surf && !golf;
}
function syncTripModeFields() {
  var surfOnly = currentTripMode === 'surf';
  // A Custom trip with Surf ticked and Golf unticked is a surf-only trip too —
  // it keeps the message box, but the golfers field has nothing to collect.
  var noGolf = surfOnly || (currentTripMode === 'custom' && customFocusIsSurfOnly());
  var golfGrp = document.getElementById('golfersGroup');
  var golfInp = document.getElementById('numGolfers');
  var row = document.getElementById('paxSplitRow');
  if (golfGrp) golfGrp.hidden = noGolf;
  if (golfInp) { golfInp.disabled = noGolf; if (noGolf) golfInp.value = ''; }
  if (row) row.classList.toggle('form-row-solo', noGolf);
  var msgGrp = document.getElementById('messageGroup');
  var msgFld = document.getElementById('messageField');
  // The notes box stays available in every mode — surf visitors just get a shorter prompt.
  if (msgGrp) msgGrp.hidden = !currentTripMode;
  if (msgFld) {
    // Disabled fields are omitted from the POST, so a hidden box never reaches
    // Formspree or the leads tracker with stale text from another tab.
    msgFld.disabled = !currentTripMode;
    if (!currentTripMode) msgFld.value = '';
    var ph = messagePlaceholderFor(currentTripMode);
    if (ph) msgFld.placeholder = ph;
  }
}
function syncRoughTiming() {
  var grp = document.getElementById('roughTimingGroup');
  var sel = document.getElementById('roughTiming');
  var tbdInp = document.getElementById('datesTbd');
  if (!grp) return;
  var show = !!currentTripMode && currentTripMode !== 'surf' && !!(tbdInp && tbdInp.value === 'yes');
  grp.hidden = !show;
  if (sel) { sel.disabled = !show; if (!show) sel.value = ''; }
}
function applyTripMode(sec) {
  currentTripMode = sec || '';
  var form = document.getElementById('contactForm');
  if (!form) return;
  var unlocked = !!sec;
  var details = document.getElementById('tripDetails');
  if (details) details.classList.toggle('step-locked', !unlocked);
  var hint = document.getElementById('stepHint');
  if (hint) hint.hidden = unlocked;
  var surfMode = sec === 'surf';
  if (window.scDatePicker) window.scDatePicker.setAllowTbd(!surfMode);
  var dateLabel = document.getElementById('dateLabel');
  // Always asked for: if the dates really are open, the picker's "I'm not sure yet"
  // toggle carries that — the field is never presented as optional.
  if (dateLabel) dateLabel.innerHTML = 'Trip Start Date <span style="color:var(--coral);">*</span>';
  var btn = form.querySelector('button[type="submit"]');
  if (btn && !btn.disabled) btn.textContent = surfMode ? 'Lock In This Estimate ' : 'Request My Quote ';
  var sticky = document.getElementById('stickyQuoteBtn');
  if (sticky) sticky.textContent = surfMode ? 'Lock In This Estimate' : 'Request My Quote';
  var surfBox = form.querySelector('input[data-package-key="wave-pool"]');
  if (surfBox && surfBox.checked !== (sec === 'surf')) {
    surfBox.checked = (sec === 'surf');
    surfBox.dispatchEvent(new Event('change', { bubbles: true }));
  }
  var addons = document.getElementById('tripAddons');
  if (addons) {
    addons.hidden = !unlocked;
    if (!unlocked) addons.querySelectorAll('[data-toggle]').forEach(function (t) { t.checked = false; });
    if (typeof window.scSyncAddons === 'function') window.scSyncAddons();
  }
  syncTripModeFields();
  syncRoughTiming();
}
(function initTripMode() {
  if (!document.getElementById('contactForm')) return;
  document.querySelectorAll('#contactForm .pkg-tab').forEach(function (t) {
    t.addEventListener('click', function () { applyTripMode(t.dataset.section); });
  });
  var startInput = document.getElementById('tripStartTimingHook') || document.getElementById('tripStartDate');
  if (startInput) startInput.addEventListener('change', syncRoughTiming);
  // Default path: Surf & Golf opens preselected (our flagship); ?package= deep
  // links run later and override this when the visitor came from a package card.
  var defTab = document.querySelector('#contactForm .pkg-tab[data-section="surf-golf"]');
  if (defTab) defTab.click(); else applyTripMode('');
})();

(function initInquiryLiveErrorClear() {
  const form = document.getElementById('contactForm');
  if (!form) return;
  const errorEl = document.getElementById('formError');
  function onEdit(e) {
    const group = e.target.closest('.form-group');
    if (group) group.classList.remove('has-error');
    const pkg = e.target.closest('.package-options');
    if (pkg) pkg.classList.remove('has-error');
    // If the error block was already shown, re-check live and hide it
    // once everything is filled in.
    if (errorEl && !errorEl.hidden) {
      const { missing } = validateInquiryForm(form);
      if (missing.length === 0) errorEl.hidden = true;
    }
  }
  form.addEventListener('input', onEdit);
  form.addEventListener('change', onEdit);
  // After a successful submit the form resets — clear any stale error UI.
  form.addEventListener('reset', () => {
    if (errorEl) errorEl.hidden = true;
    form.querySelectorAll('.has-error').forEach(el => el.classList.remove('has-error'));
  });
})();

// After a successful submission, open the visitor's mail app with a
// pre-filled draft addressed to us, so they can also reach out directly.
function openInquiryMailDraft(form) {
  try {
    const fd = new FormData(form);
    const labels = {
      first_name: 'First name',
      last_name: 'Last name',
      email: 'Email',
      whatsapp: 'WhatsApp / phone',
      custom_budget: 'Budget',
      trip_start_date: 'Trip start date',
      num_nights: 'Nights',
      adults: 'Adults',
      children: 'Children',
      children_ages: 'Children ages',
      rooms: 'Rooms',
      sessions_per_day: 'Surf sessions / day',
      private_pool_wave: 'Private pool wave setting',
      coaching_type: 'Coaching',
      coaching_sessions: 'Coaching sessions',
      private_pool_sessions: 'Private pool sessions (whole pool)',
      quoted_estimate: 'Estimate shown on the form',
      rough_timing: 'Rough timing',
      custom_surf_sessions: 'Custom — surf sessions (total)',
      custom_golf_rounds: 'Custom — golf rounds (total)',
      surf_level: 'Surf level',
      num_surfers: 'Number of surfers',
      num_golfers: 'Number of golfers',
      message: 'Notes'
    };

    const first = (fd.get('first_name') || '').toString().trim();
    const last = (fd.get('last_name') || '').toString().trim();
    const fullName = [first, last].filter(Boolean).join(' ');

    const lines = [];
    const interested = fd.getAll('interested_in').filter(Boolean);
    if (interested.length) lines.push('Interested in: ' + interested.join(', '));
    const focus = fd.getAll('custom_focus').filter(Boolean);
    if (focus.length) lines.push('Custom focus: ' + focus.join(' + '));
    Object.keys(labels).forEach(key => {
      const val = (fd.get(key) || '').toString().trim();
      if (val) lines.push(labels[key] + ': ' + val);
    });
    if ((fd.get('dates_tbd') || '').toString().trim()) lines.push('Dates: To be decided');

    const subject = 'Trip Inquiry' + (fullName ? ' — ' + fullName : '') + ' (surfchina.co)';
    const body =
      'Hello Surf China team,\n\n' +
      'I just submitted a trip inquiry on surfchina.co. Here are my details:\n\n' +
      lines.join('\n') +
      '\n\nLooking forward to hearing from you.';

    const mailto = 'mailto:hello@surfchina.co'
      + '?subject=' + encodeURIComponent(subject)
      + '&body=' + encodeURIComponent(body);

    const a = document.createElement('a');
    a.href = mailto;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } catch (_) { /* mail draft is best-effort; never block the submission flow */ }
}

function syncNameFields(form) {
  const full = form.querySelector('[name="full_name"]');
  if (!full) return;
  const parts = full.value.trim().split(/\s+/).filter(Boolean);
  const fn = form.querySelector('input[type="hidden"][name="first_name"]');
  const ln = form.querySelector('input[type="hidden"][name="last_name"]');
  if (fn) fn.value = parts.length ? parts[0] : '';
  if (ln) ln.value = parts.length > 1 ? parts.slice(1).join(' ') : '';
}
// Classify which quote entry point this visit is using — keeps GA event
// reporting to four clean buckets: main_quote (site form), package_quote
// (arrived with ?package= from a package page), book_quote (/book standalone
// form), golf_quote (golf-inquiry.html).
function quoteEntry() {
  try { if (new URLSearchParams(window.location.search).get('package')) return 'package_quote'; } catch (_) {}
  return 'main_quote';
}
async function handleSubmit(e) {
  e.preventDefault();
  const form = e.target;
  let submitted = false;
  // GA4: every "Request My Quote" click — fires even when validation fails,
  // so the click -> generate_lead funnel shows where people drop off.
  try {
    if (typeof gtag === 'function') {
      gtag('event', 'quote_cta_click', {
        form_id: 'trip_inquiry',
        quote_entry: quoteEntry(),
        page_location: window.location.href
      });
    }
  } catch (_) { /* analytics is best-effort */ }
  syncNameFields(form);
  const btn = form.querySelector('button[type="submit"]');
  const status = document.getElementById('formStatus');
  const errorEl = document.getElementById('formError');

  // Reset previous error state, then validate.
  form.querySelectorAll('.has-error').forEach(el => el.classList.remove('has-error'));
  if (errorEl) errorEl.hidden = true;
  const { missing, errorFields } = validateInquiryForm(form);
  if (missing.length) {
    if (errorEl) {
      let msg = '<strong>Please complete the following before sending:</strong><ul>';
      missing.forEach(m => { msg += '<li>' + m + '</li>'; });
      msg += '</ul>';
      errorEl.innerHTML = msg;
      errorEl.hidden = false;
    }
    errorFields.forEach(el => { if (el) el.classList.add('has-error'); });
    // Bring the error message + the first offending field into view.
    if (errorEl) errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }

  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Sending…';
  if (status) { status.style.display = 'none'; status.textContent = ''; status.style.color = ''; }
  try {
    const res = await fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    });
    if (res.ok) {
      submitted = true;
      // GA4 conversion: a real Trip Inquiry submission (capture which package, before reset).
      try {
        if (typeof gtag === 'function') {
          const fd = new FormData(form);
          gtag('event', 'generate_lead', {
            form_id: 'trip_inquiry',
            quote_entry: quoteEntry(),
            package: fd.getAll('interested_in').filter(Boolean).join(', ') || 'unspecified',
            page_location: window.location.href
          });
        }
      } catch (_) { /* analytics is best-effort */ }
      openInquiryMailDraft(form);
      form.reset();
      btn.textContent = 'Submitted';
      btn.classList.remove('btn-arrow');
      btn.classList.add('btn-success');
      btn.disabled = true;
      const sticky = document.getElementById('stickyQuoteBtn');
      if (sticky) {
        sticky.textContent = 'Submitted';
        sticky.classList.remove('btn-arrow');
        sticky.classList.add('btn-success');
        sticky.disabled = true;
      }
      if (status) {
        status.textContent = 'Thank you! We\'ll get back to you within 24–48 hours. Your email app should also open with a copy of your inquiry — feel free to send it to reach us directly.';
        status.style.color = 'var(--teal)';
        status.style.display = 'block';
      }
    } else {
      let msg = 'Something went wrong. Please email hello@surfchina.co or WhatsApp +86 138 9340 2173.';
      try {
        const data = await res.json();
        if (data && data.errors && data.errors.length) { msg = data.errors.map(x => x.message).join(' '); }
      } catch (_) {}
      if (status) {
        status.textContent = msg;
        status.style.color = '#b00020';
        status.style.display = 'block';
      } else { alert(msg); }
    }
  } catch (err) {
    const msg = 'Network error. Please email hello@surfchina.co or WhatsApp +86 138 9340 2173.';
    if (status) {
      status.textContent = msg;
      status.style.color = '#b00020';
      status.style.display = 'block';
    } else { alert(msg); }
  } finally {
    if (!submitted) {
      btn.disabled = false;
      btn.textContent = originalText;
    }
  }
}

// Route via URL hash so external pages (e.g. culture.html) can link back with #contact / #packages etc.
// Also seed the initial history entry with a state object so popstate (browser Back) can restore
// the correct internal page on the very first back press.
(function () {
  // Section deep links: a hash that is not a page but an element inside one.
  // /#training-camp opens the Surf Pool panel and scrolls to the coaching block
  // (used in partner / camp PDFs — keep it working).
  const SECTION_LINKS = { 'training-camp': 'wavepool' };
  const hash = (window.location.hash || '').replace('#', '').trim();
  const sectionPage = SECTION_LINKS[hash] || null;
  const initialPage = (hash && document.getElementById('page-' + hash)) ? hash : (sectionPage || 'home');
  try {
    window.history.replaceState({ page: initialPage }, '', window.location.href);
  } catch (e) { /* noop */ }
  if (initialPage !== 'home') {
    // Show the requested page without pushing a new entry (we just replaced the existing one).
    showPage(initialPage, true);
  }
  if (sectionPage) {
    const el = document.getElementById(hash);
    if (el) setTimeout(function () { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 300);
  }
})();

// Jump to the quote form from a package card and preselect that package (wave-pool /
// surf-golf-* / custom), or just open the matching tab (e.g. "surf-golf") so the visitor
// picks a tier. Used by the "Get a Quote" CTAs on the package cards.
function requestQuote(key) {
  // GA4: a package-card "Get a Quote" / "Start Planning" click, with which card.
  try {
    if (typeof gtag === 'function') {
      gtag('event', 'get_quote_click', {
        package: key || 'unspecified',
        page_location: window.location.href
      });
    }
  } catch (_) { /* analytics is best-effort */ }
  showPage('contact');
  var k = key ? String(key).replace(/[^a-z0-9-]/gi, '') : '';
  var form = document.getElementById('contactForm');
  if (k && form) {
    var box = form.querySelector('input[data-package-key="' + k + '"]');
    var sec = box ? box.closest('.pkg-section') : null;
    var tab = form.querySelector('.pkg-tab[data-section="' + (sec ? sec.dataset.section : k) + '"]');
    if (tab) tab.click();
    if (box) {
      box.checked = true;
      box.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }
  if (form) setTimeout(function () { form.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 250);
  return false;
}

// Pre-select a package on the quote form when arriving from a package page with
// ?package=<key> (e.g. /?package=surf-golf-premium#contact). The booking flow is an
// embedded frame now: pass the key through so it opens on the right trip.
(function () {
  var frame = document.getElementById('bywFrame');
  if (!frame) return;
  var key = '';
  try { key = new URLSearchParams(window.location.search).get('package') || ''; } catch (e) {}
  if (key) frame.src = '/book-your-wave?embed=1&package=' + encodeURIComponent(key);
  window.addEventListener('message', function (e) {
    if (e.origin !== window.location.origin || !e.data || e.data.byw == null) return;
    if (e.data.byw === 'h' && e.data.h > 0) frame.style.height = Math.ceil(e.data.h) + 'px';
    if (e.data.byw === 'h') tellScroll();
    if (e.data.byw === 'top') {
      var y = frame.getBoundingClientRect().top + window.scrollY - 84;
      window.scrollTo({ top: Math.max(0, y), behavior: 'instant' });
    }
    if (e.data.byw === 'step' && typeof e.data.n === 'number') {
      // one history entry per booking step, so Back walks the flow instead of leaving it
      try { window.history.pushState({ page: 'contact', byw: e.data.n }, '', window.location.href); } catch (err) {}
    }
    if (e.data.byw === 'mailto' && typeof e.data.url === 'string' && e.data.url.indexOf('mailto:hello@surfchina.co') === 0) {
      // the frame can't open the mail app itself — do it from the top window
      try { window.location.href = e.data.url; } catch (err) {}
    }
    if (e.data.byw === 'bar') {
      var bar = document.getElementById('bywBar');
      if (bar) { bar.hidden = !e.data.on; if (e.data.pp) document.getElementById('bywPP').textContent = e.data.pp; }
    }
    if (e.data.byw === 'scrollTo' && typeof e.data.y === 'number') {
      var yy = frame.getBoundingClientRect().top + window.scrollY + e.data.y - 120;
      window.scrollTo({ top: Math.max(0, yy), behavior: 'smooth' });
    }
  });
  // Tell the frame where it sits in our viewport (rAF-throttled) so its price rail can follow the scroll
  var scrollPending = false;
  function tellScroll() {
    if (scrollPending) return; scrollPending = true;
    requestAnimationFrame(function () {
      scrollPending = false;
      var pc = document.getElementById('page-contact');
      if (!pc || getComputedStyle(pc).display === 'none') return;
      try { frame.contentWindow.postMessage({ byw: 'scroll', top: frame.getBoundingClientRect().top }, window.location.origin); } catch (e) {}
    });
  }
  window.addEventListener('scroll', tellScroll, { passive: true });
  window.addEventListener('resize', tellScroll);
  frame.addEventListener('load', tellScroll);
  var nextBtn = document.getElementById('bywNext');
  if (nextBtn) nextBtn.addEventListener('click', function () {
    try { frame.contentWindow.postMessage({ byw: 'next' }, window.location.origin); } catch (e) {}
  });
  if (key) {
    var open = function () { if (document.getElementById('page-contact')) showPage('contact', true); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', open); else open();
  }
})();

// Gallery-strip mobile carousel: wrap each .gallery-strip and add prev/next arrows with looping
document.querySelectorAll('.gallery-strip').forEach(strip => {
  const wrap = document.createElement('div');
  wrap.className = 'gallery-strip-wrap';
  strip.parentNode.insertBefore(wrap, strip);
  wrap.appendChild(strip);

  const prev = document.createElement('button');
  prev.type = 'button';
  prev.className = 'gallery-nav gallery-nav-prev';
  prev.setAttribute('aria-label', 'Previous image');
  prev.innerHTML = '\u2039';

  const next = document.createElement('button');
  next.type = 'button';
  next.className = 'gallery-nav gallery-nav-next';
  next.setAttribute('aria-label', 'Next image');
  next.innerHTML = '\u203A';

  wrap.appendChild(prev);
  wrap.appendChild(next);

  const imgs = strip.querySelectorAll('img');

  function step(delta) {
    const n = imgs.length;
    if (!n) return;
    const gap = parseFloat(getComputedStyle(strip).gap) || 8;
    const itemW = imgs[0].getBoundingClientRect().width + gap;
    let idx = Math.round(strip.scrollLeft / itemW) + delta;
    if (idx < 0) idx = n - 1;
    if (idx >= n) idx = 0;
    strip.scrollTo({ left: idx * itemW, behavior: 'smooth' });
  }

  prev.addEventListener('click', () => step(-1));
  next.addEventListener('click', () => step(1));
});

// Private pool add-on: pick the wave first, then how many sessions. Price follows the wave.
(function initTripAddons() {
  var wrap = document.getElementById('tripAddons');
  if (!wrap) return;
  var blocks = wrap.querySelectorAll('[data-addon]');
  // Rates are held in RMB (the park bills in RMB); the form quotes in USD at the package FX.
  var money = function (rmb) { return '$' + Math.round(Number(rmb) / 7).toLocaleString(); };
  function picked(b) { return b.querySelector('input[type="radio"]:checked'); }
  function isOn(b) { var t = b.querySelector('[data-toggle]'); return !!(t && t.checked); }
  function syncBlock(b) {
    var on = isOn(b), r = picked(b), base = r || b.querySelector('input[type="radio"]');
    var priceEl = b.querySelector('[data-price]');
    var steps = b.querySelectorAll('.ppool__step');
    var count = b.querySelector('[data-count]');
    if (priceEl && base) {
      var promo = base.dataset.promo, list = base.dataset.list;
      var was = (list && list !== promo) ? ' <span class="ppool__was">' + money(list) + '</span>' : '';
      priceEl.innerHTML = (r ? '' : '<span class="ppool__unit">from</span> ') + money(promo) + was + ' <span class="ppool__unit">/ session</span>';
    }
    // Collapsed until the visitor opts in; the wave/kind choice then unlocks the count.
    if (steps[0]) steps[0].hidden = !on;
    if (steps[1]) steps[1].hidden = !on || !r;
    if (!on) {
      b.querySelectorAll('input[type="radio"]').forEach(function (x) { x.checked = false; });
      r = null;
    }
    if (count) {
      count.disabled = !on || !r;
      if (!on || !r) count.value = '0';
      else if (count.value === '0' || count.value === '') count.value = '1';
    }
    b.classList.toggle('ppool--on', on);
  }
  // Totals in RMB, so the estimator can convert once at the package FX.
  window.scAddonsRmb = function () {
    var promo = 0, list = 0, parts = [];
    blocks.forEach(function (b) {
      if (!isOn(b)) return;
      var r = picked(b), count = b.querySelector('[data-count]');
      var n = r && count ? Math.max(0, Math.round(parseFloat(count.value) || 0)) : 0;
      if (!n) return;
      promo += n * parseFloat(r.dataset.promo);
      list += n * parseFloat(r.dataset.list || r.dataset.promo);
      parts.push(n + ' ' + (b.dataset.addon === 'pool' ? 'private pool' : 'coaching') + ' session' + (n > 1 ? 's' : ''));
    });
    return { promo: promo, list: list, label: parts.join(' + ') };
  };
  window.scSyncAddons = function () { blocks.forEach(syncBlock); };
  blocks.forEach(function (b) {
    var refresh = function () { syncBlock(b); if (typeof window.scRefreshEstimate === 'function') window.scRefreshEstimate(); };
    var t = b.querySelector('[data-toggle]');
    if (t) t.addEventListener('change', refresh);
    b.querySelectorAll('input[type="radio"]').forEach(function (r) { r.addEventListener('change', refresh); });
    var c = b.querySelector('[data-count]');
    if (c) c.addEventListener('input', function () { if (typeof window.scRefreshEstimate === 'function') window.scRefreshEstimate(); });
    syncBlock(b);
  });
})();
