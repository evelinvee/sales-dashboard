/* Sales Performance Dashboard
   Loads data.json (built by build_data.py) and renders KPI cards with
   period-over-period trend, interactive Chart.js charts, and a top-products
   table — all client-side, so it runs on GitHub Pages with no backend. */

const PALETTE = ["#3b5bdb", "#15a06b", "#f08c00", "#e8590c", "#1098ad", "#7048e8", "#c2255c", "#74b816"];
const ACCENT = "#3b5bdb";
const GRID = "#eef1f6";

const usd0 = n => "$" + Math.round(n).toLocaleString("en-US");
const usd2 = n => "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const num = n => n.toLocaleString("en-US");

let DATA = null;
const charts = {};

Chart.defaults.font.family = "Inter, system-ui, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = "#69748c";

function destroy(id) { if (charts[id]) { charts[id].destroy(); delete charts[id]; } }

function setDelta(elId, pct) {
  const el = document.getElementById(elId);
  const up = pct >= 0;
  const arrow = up ? "▲" : "▼";
  el.className = "k-delta " + (up ? "up" : "down");
  el.innerHTML = `${arrow} ${Math.abs(pct).toFixed(1)}% <span class="vs">vs prior period</span>`;
}

function renderKPIs(scope) {
  const k = scope.kpis, d = scope.deltas;
  document.getElementById("kpi-revenue").textContent = usd0(k.revenue);
  document.getElementById("kpi-orders").textContent = num(k.orders);
  document.getElementById("kpi-units").textContent = num(k.units);
  document.getElementById("kpi-aov").textContent = usd2(k.aov);
  setDelta("d-revenue", d.revenue);
  setDelta("d-orders", d.orders);
  setDelta("d-units", d.units);
  setDelta("d-aov", d.aov);
}

function monthLabel(m) {
  const [y, mo] = m.split("-");
  return new Date(y, mo - 1).toLocaleDateString("en-US", { month: "short", year: "2-digit" });
}

const moneyAxis = { ticks: { callback: v => "$" + (v / 1000) + "k" }, grid: { color: GRID }, border: { display: false } };
const noGrid = { grid: { display: false }, border: { display: false } };

function renderMonth(scope) {
  destroy("month");
  const rows = scope.revenue_by_month;
  const ctx = document.getElementById("monthChart").getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 0, 300);
  g.addColorStop(0, "rgba(59,91,219,.22)"); g.addColorStop(1, "rgba(59,91,219,0)");
  charts.month = new Chart(ctx, {
    type: "line",
    data: {
      labels: rows.map(r => monthLabel(r.month)),
      datasets: [{
        data: rows.map(r => r.revenue), borderColor: ACCENT, backgroundColor: g,
        fill: true, tension: 0.35, borderWidth: 2.5, pointRadius: 0, pointHoverRadius: 5,
        pointBackgroundColor: ACCENT,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => "Revenue: " + usd0(c.parsed.y) } } },
      scales: { y: moneyAxis, x: noGrid },
    },
  });
}

function renderCategory(scope) {
  destroy("cat");
  const rows = scope.revenue_by_category;
  charts.cat = new Chart(document.getElementById("catChart"), {
    type: "doughnut",
    data: {
      labels: rows.map(r => r.category),
      datasets: [{ data: rows.map(r => r.revenue), backgroundColor: PALETTE, borderColor: "#fff", borderWidth: 2 }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: "62%",
      plugins: {
        legend: { position: "right", labels: { boxWidth: 10, boxHeight: 10, padding: 13, usePointStyle: true, pointStyle: "circle" } },
        tooltip: { callbacks: { label: c => ` ${c.label}: ${usd0(c.parsed)}` } },
      },
    },
  });
}

function renderRegion(selected) {
  destroy("region");
  const rows = DATA.scopes.All.revenue_by_region;
  charts.region = new Chart(document.getElementById("regionChart"), {
    type: "bar",
    data: {
      labels: rows.map(r => r.region),
      datasets: [{
        data: rows.map(r => r.revenue), borderRadius: 6, maxBarThickness: 54,
        backgroundColor: rows.map(r => (selected !== "All" && r.region === selected) ? ACCENT : "#c4cef0"),
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => usd0(c.parsed.y) } } },
      scales: { y: moneyAxis, x: noGrid },
    },
  });
}

function renderTable(scope) {
  const total = scope.kpis.revenue;
  const body = document.getElementById("prodBody");
  body.innerHTML = scope.top_products.map((p, i) => {
    const share = (p.revenue / total) * 100;
    return `<tr>
      <td class="rank">${i + 1}</td>
      <td class="pname">${p.product}</td>
      <td><span class="tag">${p.category}</span></td>
      <td class="num">${num(p.units)}</td>
      <td class="num">${usd0(p.revenue)}</td>
      <td class="num">${share.toFixed(1)}%<div class="bar"><i style="width:${share.toFixed(1)}%"></i></div></td>
    </tr>`;
  }).join("");
}

function render(scopeName) {
  const scope = DATA.scopes[scopeName];
  renderKPIs(scope);
  renderMonth(scope);
  renderCategory(scope);
  renderRegion(scopeName);
  renderTable(scope);
}

async function init() {
  DATA = await (await fetch("data.json")).json();
  const sel = document.getElementById("region");
  ["All", ...DATA.regions].forEach(r => {
    const o = document.createElement("option");
    o.value = r; o.textContent = (r === "All" ? "All regions" : r);
    sel.appendChild(o);
  });
  sel.addEventListener("change", e => render(e.target.value));

  // Sidebar nav: smooth-scroll (via CSS) + highlight the clicked section.
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(a => a.addEventListener("click", () => {
    navItems.forEach(n => n.classList.remove("active"));
    a.classList.add("active");
  }));

  document.getElementById("sideFoot").textContent =
    `Sample data · ${DATA.generated}`;
  document.getElementById("foot").textContent =
    `All figures in ${DATA.currency}`;
  render("All");
}

init();
