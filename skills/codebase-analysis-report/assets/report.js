/*
 * report.js — deferred interaction layer for the generated report.
 *
 * Progressive enhancement only. Every feature works without JavaScript:
 *  - Navigation is ordinary in-page anchors.
 *  - Disclosures render expanded server-side; JS adds collapse behavior.
 *  - Mermaid source is present as escaped text; JS reveals a rendered SVG
 *    only after strict rendering succeeds. Failure keeps the source visible.
 *
 * The blocking pre-paint theme initializer lives inline in <head>; this file
 * only wires the interactive controls and reacts to OS changes.
 *
 * No network calls, no external assets. Mermaid is loaded from a local file.
 */
(function () {
  "use strict";

  var THEME_KEY = "car:theme:v1"; // versioned, neutral, matches head initializer
  var VALID_THEMES = ["system", "light", "dark"];

  function safeGet(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }
  function safeSet(key, value) {
    try { window.localStorage.setItem(key, value); return true; } catch (e) { return false; }
  }

  function systemPrefersDark() {
    try { return window.matchMedia("(prefers-color-scheme: dark)").matches; }
    catch (e) { return false; }
  }

  function currentPreference() {
    var pref = safeGet(THEME_KEY);
    return VALID_THEMES.indexOf(pref) !== -1 ? pref : "system";
  }

  function resolveTheme(pref) {
    if (pref === "light") return "light";
    if (pref === "dark") return "dark";
    return systemPrefersDark() ? "dark" : "light";
  }

  function applyTheme(pref) {
    var resolved = resolveTheme(pref);
    var root = document.documentElement;
    root.setAttribute("data-theme", resolved);
    root.style.colorScheme = resolved;
    updateThemeControls(pref, resolved);
  }

  function updateThemeControls(pref, resolved) {
    var buttons = document.querySelectorAll("[data-theme-choice]");
    for (var i = 0; i < buttons.length; i++) {
      var choice = buttons[i].getAttribute("data-theme-choice");
      buttons[i].setAttribute("aria-pressed", String(choice === pref));
    }
    var status = document.getElementById("theme-status");
    if (status) {
      var label = pref === "system" ? "System (" + resolved + ")" : pref.charAt(0).toUpperCase() + pref.slice(1);
      status.textContent = "Theme: " + label;
    }
  }

  function initThemeControls() {
    var buttons = document.querySelectorAll("[data-theme-choice]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function (ev) {
        var choice = ev.currentTarget.getAttribute("data-theme-choice");
        if (VALID_THEMES.indexOf(choice) === -1) return;
        safeSet(THEME_KEY, choice);
        applyTheme(choice);
      });
    }
    // React to OS changes only when preference is System.
    try {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      var listener = function () { if (currentPreference() === "system") applyTheme("system"); };
      if (mq.addEventListener) mq.addEventListener("change", listener);
      else if (mq.addListener) mq.addListener(listener);
    } catch (e) { /* matchMedia unavailable: ignore */ }
    applyTheme(currentPreference());
  }

  /* ---- In-page nav aria-current ---- */
  function initScrollSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".sidebar nav a[href^='#']"));
    if (!links.length || !("IntersectionObserver" in window)) return;
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          links.forEach(function (a) { a.removeAttribute("aria-current"); });
          var active = byId[entry.target.id];
          if (active) active.setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    document.querySelectorAll("section.report-section[id]").forEach(function (s) { observer.observe(s); });
  }

  /* ---- Disclosures (native buttons already accessible; JS collapses) ---- */
  function initDisclosures() {
    var toggles = document.querySelectorAll("button.disclosure-toggle");
    for (var i = 0; i < toggles.length; i++) {
      var btn = toggles[i];
      var panelId = btn.getAttribute("aria-controls");
      var panel = panelId && document.getElementById(panelId);
      if (!panel) continue;
      // Collapse by default once JS is available (server rendered expanded).
      btn.setAttribute("aria-expanded", "false");
      panel.hidden = true;
      btn.addEventListener("click", function (ev) {
        var b = ev.currentTarget;
        var p = document.getElementById(b.getAttribute("aria-controls"));
        var expanded = b.getAttribute("aria-expanded") === "true";
        b.setAttribute("aria-expanded", String(!expanded));
        if (p) p.hidden = expanded;
      });
    }
  }

  /* ---- Sortable tables ---- */
  function cellValue(row, index) {
    var cell = row.children[index];
    if (!cell) return "";
    var sortVal = cell.getAttribute("data-sort");
    return (sortVal !== null ? sortVal : cell.textContent).trim();
  }

  function initSortableTables() {
    var tables = document.querySelectorAll("table[data-sortable]");
    for (var t = 0; t < tables.length; t++) {
      (function (table) {
        var headers = table.querySelectorAll("thead th");
        for (var h = 0; h < headers.length; h++) {
          (function (th, index) {
            var btn = th.querySelector("button.sort-btn");
            if (!btn) return;
            btn.addEventListener("click", function () {
              var current = th.getAttribute("aria-sort") || "none";
              var dir = current === "ascending" ? "descending" : "ascending";
              // Only sortable headers (those with a sort button) carry aria-sort.
              var allTh = table.querySelectorAll("thead th");
              for (var k = 0; k < allTh.length; k++) {
                if (allTh[k].querySelector("button.sort-btn")) allTh[k].setAttribute("aria-sort", "none");
              }
              th.setAttribute("aria-sort", dir);
              var tbody = table.tBodies[0];
              var rows = Array.prototype.slice.call(tbody.rows);
              var numeric = th.getAttribute("data-type") === "number";
              var rank = th.getAttribute("data-type") === "severity";
              var order = { critical: 0, high: 1, medium: 2, low: 3, none: 4 };
              rows.sort(function (a, b) {
                var av = cellValue(a, index), bv = cellValue(b, index);
                var cmp;
                if (numeric) { cmp = parseFloat(av || "0") - parseFloat(bv || "0"); }
                else if (rank) { cmp = (order[av] == null ? 99 : order[av]) - (order[bv] == null ? 99 : order[bv]); }
                else { cmp = av.localeCompare(bv); }
                return dir === "ascending" ? cmp : -cmp;
              });
              rows.forEach(function (r) { tbody.appendChild(r); });
            });
          })(headers[h], h);
        }
      })(tables[t]);
    }
  }

  /* ---- Filtering ---- */
  function initFilters() {
    var controls = document.querySelectorAll("[data-filter-for]");
    for (var i = 0; i < controls.length; i++) {
      (function (control) {
        var tableId = control.getAttribute("data-filter-for");
        var table = document.getElementById(tableId);
        if (!table) return;
        var attr = control.getAttribute("data-filter-attr");
        var statusEl = document.getElementById(control.getAttribute("data-filter-status"));
        function apply() {
          var value = (control.value || "").toLowerCase();
          var tbody = table.tBodies[0];
          var rows = Array.prototype.slice.call(tbody.rows);
          var shown = 0;
          rows.forEach(function (row) {
            var match;
            if (attr) {
              var rv = (row.getAttribute("data-" + attr) || "").toLowerCase();
              match = !value || value === "all" || rv === value;
            } else {
              match = !value || row.textContent.toLowerCase().indexOf(value) !== -1;
            }
            row.hidden = !match;
            if (match) shown++;
          });
          if (statusEl) statusEl.textContent = shown + " of " + rows.length + " rows shown";
        }
        control.addEventListener("input", apply);
        control.addEventListener("change", apply);
        apply();
      })(controls[i]);
    }
  }

  /* ---- Mermaid strict rendering with static fallback ---- */
  function initMermaid() {
    var diagrams = document.querySelectorAll(".diagram[data-mermaid-safe='true']");
    if (!diagrams.length) return;
    if (typeof window.mermaid === "undefined") return; // keep source fallback
    try {
      window.mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        theme: "neutral",
        deterministicIds: true,
        htmlLabels: false,
        flowchart: { htmlLabels: false },
        class: { htmlLabels: false }
      });
    } catch (e) { return; }

    diagrams.forEach(function (diagram, i) {
      var sourceEl = diagram.querySelector(".mermaid-source code");
      var rendered = diagram.querySelector(".mermaid-rendered");
      if (!sourceEl || !rendered) return;
      var code = sourceEl.textContent;
      var id = "mmd-" + i;
      try {
        var result = window.mermaid.render(id, code);
        if (result && typeof result.then === "function") {
          result.then(function (out) { reveal(diagram, rendered, out.svg); })
                .catch(function () { renderFailed(diagram); });
        } else if (result && result.svg) {
          reveal(diagram, rendered, result.svg);
        } else if (typeof result === "string") {
          reveal(diagram, rendered, result);
        }
      } catch (e) { renderFailed(diagram); }
    });
  }

  function reveal(diagram, rendered, svg) {
    rendered.innerHTML = svg;
    rendered.hidden = false;
    rendered.removeAttribute("aria-hidden");
    var label = diagram.querySelector(".diagram-fallback-label");
    // The escaped source is intentionally retained below the rendered SVG so
    // print and assistive technology always have the authoritative text.
    if (label) label.textContent = "Diagram rendered. Source available below.";
  }

  function renderFailed(diagram) {
    // JS is present but rendering failed: keep the source and say why.
    var label = diagram.querySelector(".diagram-fallback-label");
    if (label) label.textContent = "Diagram could not be rendered; source shown below.";
  }

  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  ready(function () {
    initThemeControls();
    initScrollSpy();
    initDisclosures();
    initSortableTables();
    initFilters();
    initMermaid();
  });
})();
