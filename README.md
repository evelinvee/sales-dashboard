# 📊 Sales Dashboard

An interactive e-commerce sales dashboard. A Python script generates a realistic synthetic dataset and aggregates it into `data.json`; a static HTML/CSS/JavaScript frontend loads that file and renders KPIs and Chart.js charts with a region filter. Fully static, so it runs on GitHub Pages with no backend.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-vanilla-F7DF1E?logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?logo=chartdotjs&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-3b5bdb)

> **View it live:** https://evelinvee.github.io/sales-dashboard/ — KPI cards with period-over-period trend, revenue charts, and a region filter. All data is synthetic, for demonstration.

---

## ✨ Features

- **KPI cards** — revenue, orders, units and average order value, each with a period-over-period trend indicator
- **Revenue trend** — 18-month line chart with a Q4 holiday peak
- **Revenue by category** — doughnut breakdown across five categories
- **Revenue by region** — comparison across all regions, highlighting the selected one
- **Top products** table with units, revenue and revenue share
- **Region filter** recomputes every chart instantly — no backend needed
- Fully **responsive** for desktop and mobile

## ▶️ Run it

Regenerate the dataset (optional — `data.json` is already committed):

```bash
pip install -r requirements.txt
python build_data.py
```

Then serve the folder and open it in a browser:

```bash
python -m http.server 8000
# http://localhost:8000
```

**Live:** https://evelinvee.github.io/sales-dashboard/

## 🗂️ Structure

```
build_data.py     # generates the synthetic dataset -> data.json
data.json         # aggregated data the frontend reads
index.html        # dashboard markup
style.css         # styling
app.js            # Chart.js rendering + region filter
requirements.txt
LICENSE
```

## 🛠️ Tech

Python (NumPy) · vanilla JavaScript · Chart.js · HTML · CSS. Static frontend, no backend.

## 📄 License

MIT © [evelinvee](https://github.com/evelinvee)
