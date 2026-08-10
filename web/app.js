/**
 * Berlin Gigs — PWA app logic
 * Vanilla JS, no frameworks, no external deps.
 */

// ─── Constants ────────────────────────────────────────────────────────────────

const EVENTS_URL = "events.json";

const TAG_LABELS = {
  jazz: "Jazz",
  electronic: "Electronic",
  live: "Live",
  bar: "Bar / Club",
};

const TAG_COLORS = {
  jazz:       { bg: "#1a2e4a", text: "#7ec8e3" },
  electronic: { bg: "#1a1a2e", text: "#a78bfa" },
  live:       { bg: "#1a2e1a", text: "#86efac" },
  bar:        { bg: "#2e1a1a", text: "#fca5a5" },
};

const DISCOVER_VENUES = [
  {
    name: "Quasimodo",
    neighbourhood: "Charlottenburg",
    tag: "jazz",
    description: "Berlin's most storied jazz club. Intimate basement, world-class acts since 1975.",
    url: "https://www.quasimodo.de",
  },
  {
    name: "Yorckschlösschen",
    neighbourhood: "Kreuzberg",
    tag: "jazz",
    description: "A neighbourhood jazz pub with live music most nights. Beer, blues, and good company.",
    url: "https://www.yorckschloesschen.de",
  },
  {
    name: "Acud Macht Neu",
    neighbourhood: "Mitte",
    tag: "live",
    description: "Multi-space arts venue: experimental music, film screenings, theatre. Always unusual.",
    url: "https://acudmachtneu.de",
  },
  {
    name: "Urban Spree",
    neighbourhood: "Friedrichshain",
    tag: "live",
    description: "Eclectic indoor/outdoor venue. Indie, punk, electronic, art openings — all under one roof.",
    url: "https://www.urbanspree.com",
  },
  {
    name: "Traumabar und Kino",
    neighbourhood: "Mitte",
    tag: "bar",
    description: "Tiny bar with a cinema screen and adventurous music programming. Very Berlin.",
    url: "https://www.traumabar.de",
  },
];

// ─── State ────────────────────────────────────────────────────────────────────

let allEvents = [];
let activeFilter = "all";
let activeTab = "week";

// ─── Date helpers ─────────────────────────────────────────────────────────────

function today() {
  return new Date().toISOString().slice(0, 10);
}

function inDays(n) {
  const d = new Date();
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

function formatDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

function isThisWeek(dateStr) {
  return dateStr >= today() && dateStr <= inDays(7);
}

function isUpcoming(dateStr) {
  return dateStr >= today() && dateStr <= inDays(30);
}

// ─── Render helpers ───────────────────────────────────────────────────────────

function tagChip(tag) {
  const c = TAG_COLORS[tag] || TAG_COLORS.live;
  return `<span class="chip" style="background:${c.bg};color:${c.text}">${TAG_LABELS[tag] || tag}</span>`;
}

function eventCard(ev) {
  const chip = tagChip(ev.venue_tag);
  const time = ev.time ? ` · ${ev.time}` : "";
  const price = ev.price ? `<span class="price">${ev.price}</span>` : "";
  const img = ev.image_url
    ? `<img class="card-img" src="${ev.image_url}" alt="" loading="lazy">`
    : "";

  return `
    <article class="card" data-tag="${ev.venue_tag}">
      ${img}
      <div class="card-body">
        <div class="card-meta">
          ${chip}
          <span class="venue-name">${ev.venue}</span>
        </div>
        <h3 class="card-title">${ev.title}</h3>
        <div class="card-date">${formatDate(ev.date)}${time} ${price}</div>
        ${ev.description ? `<p class="card-desc">${ev.description}</p>` : ""}
        <a class="btn-tickets" href="${ev.url}" target="_blank" rel="noopener">
          More info / Tickets ↗
        </a>
      </div>
    </article>`;
}

function discoverCard(v) {
  const c = TAG_COLORS[v.tag] || TAG_COLORS.live;
  return `
    <article class="discover-card">
      <div class="card-meta">
        <span class="chip" style="background:${c.bg};color:${c.text}">${TAG_LABELS[v.tag] || v.tag}</span>
        <span class="venue-name">${v.neighbourhood}</span>
      </div>
      <h3 class="card-title">${v.name}</h3>
      <p class="card-desc">${v.description}</p>
      <a class="btn-tickets" href="${v.url}" target="_blank" rel="noopener">Visit website ↗</a>
    </article>`;
}

// ─── Main render ──────────────────────────────────────────────────────────────

function filteredEvents() {
  const pool = activeTab === "week"
    ? allEvents.filter((e) => isThisWeek(e.date))
    : allEvents.filter((e) => isUpcoming(e.date));

  if (activeFilter === "all") return pool;
  return pool.filter((e) => e.venue_tag === activeFilter);
}

function render() {
  const list = document.getElementById("event-list");
  const empty = document.getElementById("empty-state");

  if (activeTab === "discover") {
    list.innerHTML = DISCOVER_VENUES.map(discoverCard).join("");
    empty.hidden = true;
    return;
  }

  const events = filteredEvents();
  if (events.length === 0) {
    list.innerHTML = "";
    empty.hidden = false;
    return;
  }
  empty.hidden = true;

  // Group by date
  const byDate = {};
  for (const ev of events) {
    byDate[ev.date] = byDate[ev.date] || [];
    byDate[ev.date].push(ev);
  }

  const html = Object.entries(byDate)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, evs]) => `
      <div class="date-group">
        <h2 class="date-header">${formatDate(date)}</h2>
        ${evs.map(eventCard).join("")}
      </div>`)
    .join("");

  list.innerHTML = html;
}

// ─── Tab + filter wiring ──────────────────────────────────────────────────────

function setTab(tab) {
  activeTab = tab;
  document.querySelectorAll(".tab-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.tab === tab);
  });
  const filterBar = document.getElementById("filter-bar");
  filterBar.style.display = tab === "discover" ? "none" : "";
  render();
}

function setFilter(tag) {
  activeFilter = tag;
  document.querySelectorAll(".filter-pill").forEach((p) => {
    p.classList.toggle("active", p.dataset.tag === tag);
  });
  render();
}

// ─── Data loading ─────────────────────────────────────────────────────────────

async function loadEvents() {
  const status = document.getElementById("load-status");
  try {
    const resp = await fetch(EVENTS_URL + "?t=" + Date.now());
    if (!resp.ok) throw new Error(resp.statusText);
    allEvents = await resp.json();
    allEvents.sort((a, b) => a.date.localeCompare(b.date));
    status.hidden = true;
    render();
    updateBadge();
  } catch (err) {
    status.textContent = "⚠ Could not load events. Showing cached data if available.";
    status.classList.add("error");
    // Try to render from cache (service worker may have it)
    render();
  }
}

function updateBadge() {
  const thisWeek = allEvents.filter((e) => isThisWeek(e.date));
  const badge = document.getElementById("week-count");
  if (badge && thisWeek.length > 0) {
    badge.textContent = thisWeek.length;
    badge.hidden = false;
  }
}

// ─── Service worker registration ──────────────────────────────────────────────

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}

// ─── Boot ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  // Tab buttons
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => setTab(btn.dataset.tab));
  });

  // Filter pills
  document.querySelectorAll(".filter-pill").forEach((pill) => {
    pill.addEventListener("click", () => setFilter(pill.dataset.tag));
  });

  loadEvents();
});
