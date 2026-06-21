"""
Build the e-commerce dashboard dataset.

Generates a synthetic but realistic set of orders (seasonality, regional mix,
per-product pricing, an upward growth trend), aggregates everything the
dashboard needs, and writes it to data.json — which the static frontend loads
(so it runs on GitHub Pages with no backend).

Run:  python build_data.py   ->   data.json
"""

import json
import datetime as dt
import numpy as np

RNG = np.random.default_rng(7)

REGIONS = ["North America", "Europe", "Asia", "Latin America"]
REGION_WEIGHT = [0.36, 0.28, 0.26, 0.10]

# category -> products -> unit price
CATALOG = {
    "Electronics": {"Wireless Headphones": 89, "Smartwatch": 159, "Laptop": 940, "Smartphone": 620, "Bluetooth Speaker": 55},
    "Home":        {"Desk Lamp": 34, "Blender": 72, "Office Chair": 180, "Coffee Maker": 95},
    "Fashion":     {"Sneakers": 110, "Denim Jacket": 78, "Backpack": 60, "Sunglasses": 45},
    "Sports":      {"Yoga Mat": 28, "Dumbbell Set": 120, "Water Bottle": 18, "Running Shoes": 130},
    "Books":       {"Novel": 15, "Cookbook": 25, "Sci-Fi Box Set": 48},
}
CAT_WEIGHT = {"Electronics": 0.34, "Home": 0.18, "Fashion": 0.22, "Sports": 0.16, "Books": 0.10}

# 18 months of data
START = dt.date(2024, 1, 1)
MONTHS = 18
N_ORDERS = 6000

products = [(c, p, price) for c, items in CATALOG.items() for p, price in items.items()]
prod_names = [p for _, p, _ in products]
prod_cat = {p: c for c, p, _ in products}
prod_price = {p: pr for _, p, pr in products}
prod_weight = np.array([CAT_WEIGHT[c] / len(CATALOG[c]) for c, _, _ in products])
prod_weight /= prod_weight.sum()


def season_factor(month_idx):
    # gentle yearly cycle + strong Q4 (Nov/Dec) holiday bump
    m = (START.month - 1 + month_idx) % 12  # 0=Jan
    base = 1.0 + 0.12 * np.sin((m / 12) * 2 * np.pi)
    if m in (10, 11):  # Nov, Dec
        base *= 1.45
    return base


def make_orders():
    # How likely an order falls in each month: seasonality times a gentle
    # upward growth trend, so the business shows believable momentum.
    month_w = np.array([season_factor(i) * (1 + 0.5 * i / (MONTHS - 1)) for i in range(MONTHS)])
    month_w /= month_w.sum()

    orders = []
    for _ in range(N_ORDERS):
        midx = int(RNG.choice(MONTHS, p=month_w))
        y = START.year + (START.month - 1 + midx) // 12
        mo = (START.month - 1 + midx) % 12 + 1
        day = int(RNG.integers(1, 28))
        date = dt.date(y, mo, day)

        prod = RNG.choice(prod_names, p=prod_weight)
        cat = prod_cat[prod]
        price = prod_price[prod]
        qty = int(RNG.integers(1, 4)) if price < 150 else 1
        region = RNG.choice(REGIONS, p=REGION_WEIGHT)
        # seasonality occasionally adds an extra unit
        if RNG.random() < (season_factor(midx) - 1.0):
            qty += 1
        orders.append({"date": date.isoformat(), "month": date.strftime("%Y-%m"),
                       "weekday": date.weekday(), "product": prod, "category": cat,
                       "region": region, "qty": qty, "revenue": round(qty * price, 2)})
    return orders


def aggregate(orders):
    """Return a dashboard slice for a list of orders."""
    rev = sum(o["revenue"] for o in orders)
    units = sum(o["qty"] for o in orders)
    n = len(orders)

    def group_sum(key):
        d = {}
        for o in orders:
            d[o[key]] = d.get(o[key], 0) + o["revenue"]
        return d

    by_month = group_sum("month")
    months = sorted(by_month)
    by_cat = group_sum("category")
    by_region = group_sum("region")

    prod_rev, prod_units = {}, {}
    for o in orders:
        prod_rev[o["product"]] = prod_rev.get(o["product"], 0) + o["revenue"]
        prod_units[o["product"]] = prod_units.get(o["product"], 0) + o["qty"]
    top = sorted(prod_rev, key=prod_rev.get, reverse=True)[:8]

    # Period-over-period: split the timeline in half (recent vs prior) and
    # report the percentage change for each KPI, so cards can show a trend.
    half = len(months) // 2
    prior_months, recent_months = set(months[:half]), set(months[half:])

    def split_metrics(month_set):
        sub = [o for o in orders if o["month"] in month_set]
        r = sum(o["revenue"] for o in sub)
        u = sum(o["qty"] for o in sub)
        c = len(sub)
        return {"revenue": r, "orders": c, "units": u, "aov": (r / c if c else 0)}

    prior, recent = split_metrics(prior_months), split_metrics(recent_months)

    def pct(cur, prev):
        return round((cur - prev) / prev * 100, 1) if prev else 0.0

    deltas = {k: pct(recent[k], prior[k]) for k in ("revenue", "orders", "units", "aov")}

    return {
        "kpis": {"revenue": round(rev, 2), "orders": n, "units": units,
                 "aov": round(rev / n, 2) if n else 0},
        "deltas": deltas,
        "revenue_by_month": [{"month": m, "revenue": round(by_month[m], 2)} for m in months],
        "revenue_by_category": [{"category": c, "revenue": round(v, 2)}
                                for c, v in sorted(by_cat.items(), key=lambda x: -x[1])],
        "revenue_by_region": [{"region": r, "revenue": round(by_region.get(r, 0), 2)} for r in REGIONS],
        "top_products": [{"product": p, "category": prod_cat[p], "revenue": round(prod_rev[p], 2),
                          "units": prod_units[p]} for p in top],
    }


def main():
    orders = make_orders()
    data = {
        "generated": dt.datetime.now().strftime("%Y-%m-%d"),
        "currency": "USD",
        "note": "Synthetic e-commerce data generated by build_data.py — for demo purposes.",
        "regions": REGIONS,
        "scopes": {"All": aggregate(orders)},
    }
    for r in REGIONS:
        data["scopes"][r] = aggregate([o for o in orders if o["region"] == r])

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    k = data["scopes"]["All"]["kpis"]
    print(f"Wrote data.json — {len(orders)} orders | "
          f"revenue ${k['revenue']:,.0f} | {k['orders']} orders | AOV ${k['aov']:.2f}")


if __name__ == "__main__":
    main()
