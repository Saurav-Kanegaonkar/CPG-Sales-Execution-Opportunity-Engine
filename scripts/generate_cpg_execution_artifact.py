import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
OUTPUTS = ANALYSIS / "outputs"
SRC = ROOT / "src"
DOCS = ROOT / "docs" / "images"

random.seed(88217)


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def money(value):
    return round(value, 2)


retailers = [
    ("RTL01", "MetroMart", "Grocery", 0.92),
    ("RTL02", "Value Basket", "Mass", 1.12),
    ("RTL03", "FreshWay", "Grocery", 0.84),
    ("RTL04", "ClubPoint", "Club", 1.24),
    ("RTL05", "Corner Market", "Convenience", 0.68),
    ("RTL06", "ShopSquare", "Omnichannel", 1.04),
]

regions = ["Northeast", "Midwest", "South", "West"]
categories = [
    ("CAT01", "Condiments", 0.42, 1.10),
    ("CAT02", "Meals", 0.36, 0.96),
    ("CAT03", "Cheese", 0.34, 0.90),
    ("CAT04", "Cold Cuts", 0.31, 0.82),
    ("CAT05", "Coffee", 0.39, 0.78),
]

skus = []
for cat_id, category, margin_rate, velocity_index in categories:
    for i in range(1, 5):
        sku_id = f"{cat_id}-SKU{i}"
        skus.append(
            {
                "sku_id": sku_id,
                "category_id": cat_id,
                "category": category,
                "sku_name": f"{category} Item {i}",
                "margin_rate": margin_rate + random.uniform(-0.04, 0.04),
                "velocity_index": velocity_index * random.uniform(0.82, 1.22),
            }
        )

stores = []
for retailer_id, retailer, channel, scale in retailers:
    for region in regions:
        for i in range(1, 7):
            stores.append(
                {
                    "store_id": f"{retailer_id}-{region[:2].upper()}-{i:02d}",
                    "retailer_id": retailer_id,
                    "retailer": retailer,
                    "channel": channel,
                    "region": region,
                    "store_format": random.choice(["Flagship", "Core", "Small format", "Ecommerce node"]),
                    "trade_area_index": round(scale * random.uniform(0.72, 1.28), 2),
                }
            )

start = date(2025, 9, 1)
weeks = [start + timedelta(days=7 * i) for i in range(28)]

pos_rows = []
field_visits = []
validation_checks = []
promo_calendar = []

for sku in skus:
    for retailer_id, retailer, channel, _ in retailers:
        promo_calendar.append(
            {
                "promo_id": f"PROMO-{sku['sku_id']}-{retailer_id}",
                "sku_id": sku["sku_id"],
                "retailer_id": retailer_id,
                "retailer": retailer,
                "planned_feature_weeks": random.randint(3, 8),
                "planned_display_weeks": random.randint(2, 7),
                "trade_rate": round(random.uniform(0.08, 0.22), 3),
            }
        )

for week_index, week in enumerate(weeks):
    seasonality = 1 + 0.10 * math.sin((week_index / len(weeks)) * math.pi * 2)
    for store in stores:
        for sku in skus:
            base_acv = random.uniform(62, 97)
            category_pressure = 1 - (0.06 if sku["category"] in ["Cold Cuts", "Coffee"] else 0)
            distribution = max(35, min(99, base_acv * category_pressure + random.uniform(-8, 6)))
            oos_rate = max(0.01, min(0.24, random.gauss(0.065, 0.035) + (0.06 if distribution < 70 else 0)))
            promo_compliance = max(0.35, min(1.0, random.gauss(0.78, 0.14)))
            feature_support = max(0, min(1, promo_compliance + random.uniform(-0.25, 0.12)))
            display_support = max(0, min(1, promo_compliance + random.uniform(-0.22, 0.16)))
            unit_velocity = (
                sku["velocity_index"]
                * float(store["trade_area_index"])
                * seasonality
                * random.uniform(18, 46)
                * (distribution / 100)
                * (1 - oos_rate)
                * (1 + feature_support * 0.18 + display_support * 0.14)
            )
            price = random.uniform(3.4, 8.9)
            units = max(0, int(unit_velocity))
            dollar_sales = units * price
            shipment_lag_days = max(0, int(random.gauss(3, 2) + (3 if oos_rate > 0.12 else 0)))
            pos_rows.append(
                {
                    "week_start": str(week),
                    "store_id": store["store_id"],
                    "retailer": store["retailer"],
                    "channel": store["channel"],
                    "region": store["region"],
                    "sku_id": sku["sku_id"],
                    "category": sku["category"],
                    "acv_distribution": round(distribution, 1),
                    "oos_rate": round(oos_rate, 4),
                    "promo_compliance": round(promo_compliance, 3),
                    "feature_support": round(feature_support, 3),
                    "display_support": round(display_support, 3),
                    "units": units,
                    "dollar_sales": money(dollar_sales),
                    "gross_margin": money(dollar_sales * sku["margin_rate"]),
                    "shipment_lag_days": shipment_lag_days,
                }
            )

for store in random.sample(stores, 60):
    field_visits.append(
        {
            "visit_id": f"VIS-{store['store_id']}",
            "store_id": store["store_id"],
            "retailer": store["retailer"],
            "region": store["region"],
            "visit_date": str(start + timedelta(days=random.randint(0, 195))),
            "issue_found": random.choice(["void gap", "display not built", "promo tag missing", "low shelf inventory", "planogram drift"]),
            "rep_capacity_hours": round(random.uniform(1.5, 5.5), 1),
            "status": random.choice(["open", "open", "resolved", "scheduled"]),
        }
    )

check_names = ["POS freshness", "store master match", "SKU hierarchy", "promo calendar join", "shipment reconciliation", "ACV null check"]
for retailer_id, retailer, channel, _ in retailers:
    for check in check_names:
        failure_rate = max(0, random.gauss(0.035, 0.025) + (0.04 if check == "promo calendar join" and channel == "Convenience" else 0))
        validation_checks.append(
            {
                "retailer": retailer,
                "check_name": check,
                "failure_rate": round(failure_rate, 4),
                "rows_checked": random.randint(18000, 124000),
                "owner": random.choice(["BI Engineering", "Sales Analytics", "Commercial Data Ops"]),
                "status": "Investigate" if failure_rate > 0.06 else "Monitor" if failure_rate > 0.025 else "Pass",
            }
        )

rollup = defaultdict(lambda: defaultdict(float))
for row in pos_rows:
    key = (row["retailer"], row["region"], row["category"])
    values = rollup[key]
    values["dollar_sales"] += float(row["dollar_sales"])
    values["gross_margin"] += float(row["gross_margin"])
    values["units"] += int(row["units"])
    values["acv_distribution"] += float(row["acv_distribution"])
    values["oos_rate"] += float(row["oos_rate"])
    values["promo_compliance"] += float(row["promo_compliance"])
    values["feature_support"] += float(row["feature_support"])
    values["display_support"] += float(row["display_support"])
    values["shipment_lag_days"] += float(row["shipment_lag_days"])
    values["rows"] += 1

open_visits = defaultdict(int)
for visit in field_visits:
    if visit["status"] != "resolved":
        open_visits[(visit["retailer"], visit["region"])] += 1

validation_by_retailer = defaultdict(list)
for check in validation_checks:
    validation_by_retailer[check["retailer"]].append(float(check["failure_rate"]))

opportunities = []
for (retailer, region, category), values in rollup.items():
    rows = values["rows"]
    avg_distribution = values["acv_distribution"] / rows
    avg_oos = values["oos_rate"] / rows
    avg_compliance = values["promo_compliance"] / rows
    avg_feature = values["feature_support"] / rows
    avg_display = values["display_support"] / rows
    avg_lag = values["shipment_lag_days"] / rows
    margin_rate = values["gross_margin"] / values["dollar_sales"] if values["dollar_sales"] else 0
    distribution_gap = max(0, 92 - avg_distribution)
    velocity_gap = max(0, 0.84 - avg_compliance) * 100
    oos_gap = max(0, avg_oos - 0.055) * 100
    promo_gap = max(0, 0.82 - ((avg_feature + avg_display) / 2)) * 100
    data_penalty = sum(validation_by_retailer[retailer]) / len(validation_by_retailer[retailer]) * 100
    capacity_penalty = open_visits[(retailer, region)] * 1.8
    weekly_sales = values["dollar_sales"] / len(weeks)
    opportunity_value = values["dollar_sales"] * (distribution_gap * 0.007 + oos_gap * 0.018 + promo_gap * 0.012) * margin_rate * 5.2
    priority_score = distribution_gap * 0.62 + velocity_gap * 0.28 + oos_gap * 1.25 + promo_gap * 0.54 + data_penalty * 0.7 + capacity_penalty
    opportunities.append(
        {
            "retailer": retailer,
            "region": region,
            "category": category,
            "dollar_sales": money(values["dollar_sales"]),
            "gross_margin": money(values["gross_margin"]),
            "avg_acv_distribution": round(avg_distribution, 1),
            "avg_oos_rate": round(avg_oos, 4),
            "avg_promo_compliance": round(avg_compliance, 3),
            "avg_feature_display": round((avg_feature + avg_display) / 2, 3),
            "avg_shipment_lag_days": round(avg_lag, 1),
            "open_field_actions": open_visits[(retailer, region)],
            "opportunity_value": money(opportunity_value),
            "priority_score": round(priority_score, 1),
            "tier": "Critical" if priority_score >= 29 else "Watch" if priority_score >= 23 else "Stable",
            "recommended_action": "Close distribution and shelf execution gap" if priority_score >= 29 else "Validate promo and field follow-up" if priority_score >= 23 else "Track in monthly cadence",
        }
    )

opportunities.sort(key=lambda row: row["priority_score"], reverse=True)

retailer_summary = []
for retailer_id, retailer, channel, _ in retailers:
    rows = [row for row in opportunities if row["retailer"] == retailer]
    retailer_summary.append(
        {
            "retailer": retailer,
            "channel": channel,
            "opportunity_value": money(sum(float(row["opportunity_value"]) for row in rows)),
            "avg_priority_score": round(sum(float(row["priority_score"]) for row in rows) / len(rows), 1),
            "critical_count": sum(1 for row in rows if row["tier"] == "Critical"),
            "avg_distribution": round(sum(float(row["avg_acv_distribution"]) for row in rows) / len(rows), 1),
            "avg_oos_rate": round(sum(float(row["avg_oos_rate"]) for row in rows) / len(rows), 4),
        }
    )
retailer_summary.sort(key=lambda row: row["opportunity_value"], reverse=True)

category_summary = []
for _, category, margin_rate, _ in categories:
    rows = [row for row in opportunities if row["category"] == category]
    category_summary.append(
        {
            "category": category,
            "opportunity_value": money(sum(float(row["opportunity_value"]) for row in rows)),
            "avg_priority_score": round(sum(float(row["priority_score"]) for row in rows) / len(rows), 1),
            "critical_count": sum(1 for row in rows if row["tier"] == "Critical"),
            "margin_rate": round(margin_rate, 2),
        }
    )
category_summary.sort(key=lambda row: row["opportunity_value"], reverse=True)

DATA.mkdir(exist_ok=True)
ANALYSIS.mkdir(exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)
SRC.mkdir(exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

write_csv(DATA / "stores.csv", stores, list(stores[0].keys()))
write_csv(DATA / "skus.csv", skus, list(skus[0].keys()))
write_csv(DATA / "weekly_retail_execution.csv", pos_rows, list(pos_rows[0].keys()))
write_csv(DATA / "promotion_calendar.csv", promo_calendar, list(promo_calendar[0].keys()))
write_csv(DATA / "field_visits.csv", field_visits, list(field_visits[0].keys()))
write_csv(DATA / "validation_checks.csv", validation_checks, list(validation_checks[0].keys()))
write_csv(OUTPUTS / "retail_execution_opportunity_queue.csv", opportunities, list(opportunities[0].keys()))
write_csv(OUTPUTS / "retailer_summary.csv", retailer_summary, list(retailer_summary[0].keys()))
write_csv(OUTPUTS / "category_summary.csv", category_summary, list(category_summary[0].keys()))

payload = {
    "kpis": {
        "stores": len(stores),
        "skus": len(skus),
        "weeklyRows": len(pos_rows),
        "totalSales": round(sum(float(row["dollar_sales"]) for row in pos_rows)),
        "totalOpportunity": round(sum(float(row["opportunity_value"]) for row in opportunities)),
        "critical": sum(1 for row in opportunities if row["tier"] == "Critical"),
        "checksInvestigate": sum(1 for row in validation_checks if row["status"] == "Investigate"),
    },
    "opportunities": opportunities[:18],
    "retailers": retailer_summary,
    "categories": category_summary,
    "checks": sorted(validation_checks, key=lambda row: float(row["failure_rate"]), reverse=True),
    "visits": sorted(field_visits, key=lambda row: row["status"])[:14],
}

(SRC / "data.js").write_text("window.CPG_DATA = " + json.dumps(payload, indent=2) + ";\n")

(ROOT / "index.html").write_text(
    """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>CPG Sales Execution Opportunity Engine</title>
  <link rel=\"stylesheet\" href=\"src/styles.css\">
</head>
<body>
  <main id=\"app\"></main>
  <script src=\"src/data.js\"></script>
  <script src=\"src/app.js\"></script>
</body>
</html>
"""
)

(ANALYSIS / "analysis_plan.md").write_text(
    """# Analysis Plan

1. Create a weekly store, retailer, region, SKU, and category grain for retail execution analysis.
2. Integrate POS sales, ACV distribution, out-of-stock rate, promotion compliance, feature and display support, shipment lag, field visits, and validation checks.
3. Score sales execution opportunities with an explainable model that estimates margin-weighted value and action urgency.
4. Produce executive, opportunity queue, retail problem modeling, data validation, and field enablement surfaces.
"""
)

(ANALYSIS / "methodology.md").write_text(
    """# Methodology

The opportunity score estimates where field sales and commercial analytics attention can unlock the largest execution value. It weights distribution gap, promotion compliance, out-of-stock risk, feature and display support, data quality, and open field capacity. Opportunity value is margin weighted so the queue favors actions that matter commercially, not just operationally.
"""
)

(ANALYSIS / "executive_findings.md").write_text(
    f"""# Executive Findings

- The engine identified {payload['kpis']['critical']} critical retailer-region-category opportunities.
- Estimated margin-weighted opportunity is ${payload['kpis']['totalOpportunity']:,}.
- The highest value opportunity is {opportunities[0]['retailer']} in {opportunities[0]['region']} for {opportunities[0]['category']}.
- {payload['kpis']['checksInvestigate']} validation checks are marked Investigate, so sales enablement outputs should include data confidence context.
"""
)

(ANALYSIS / "sql_checks.sql").write_text(
    """-- Snowflake-style retail execution validation checks
select retailer, region, category, count(*) as weekly_rows
from weekly_retail_execution
group by retailer, region, category
having count(*) = 0;

select retailer, check_name, failure_rate
from validation_checks
where failure_rate > 0.06;

select store_id, sku_id, week_start
from weekly_retail_execution
where acv_distribution < 0
   or acv_distribution > 100
   or oos_rate < 0
   or promo_compliance < 0
   or promo_compliance > 1;

select retailer, region, category, sum(dollar_sales) as sales, sum(gross_margin) as margin
from weekly_retail_execution
group by retailer, region, category;
"""
)

(DATA / "README.md").write_text(
    """# Data

The data is synthetic and generated by `scripts/generate_cpg_execution_artifact.py` with a fixed random seed. It models a CPG retail execution environment with syndicated-style POS, store master, SKU master, promotion, field visit, and validation records.

Files:

- `stores.csv`: retailer, region, channel, format, and trade area attributes.
- `skus.csv`: category, SKU, margin, and velocity assumptions.
- `weekly_retail_execution.csv`: weekly POS and execution measures.
- `promotion_calendar.csv`: planned feature and display support.
- `field_visits.csv`: field sales follow-up records.
- `validation_checks.csv`: data quality and reconciliation checks.
"""
)

(ROOT / "data_dictionary.md").write_text(
    """# Data Dictionary

## weekly_retail_execution.csv

- `acv_distribution`: weighted distribution percentage.
- `oos_rate`: out-of-stock rate.
- `promo_compliance`: execution compliance for active promotion support.
- `feature_support`: modeled feature support.
- `display_support`: modeled display support.
- `shipment_lag_days`: days between expected replenishment signal and observed shipment update.

## analysis/outputs/retail_execution_opportunity_queue.csv

- `opportunity_value`: margin-weighted estimate of execution upside.
- `priority_score`: action urgency score based on distribution, velocity, OOS, promotion, data quality, and field capacity.
- `tier`: Critical, Watch, or Stable.
"""
)

(ROOT / "STATUS.md").write_text(
    """# Status

Portfolio artifact upgraded into a retail execution opportunity engine with generated synthetic data, scored commercial opportunities, validation checks, Snowflake-style SQL, analysis notes, and README documentation.
"""
)

print(f"Generated {len(pos_rows)} weekly retail execution rows and {len(opportunities)} scored opportunities.")
