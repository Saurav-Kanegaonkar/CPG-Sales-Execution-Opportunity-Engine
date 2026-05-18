import csv
from pathlib import Path


queue_path = Path("analysis/outputs/retail_execution_opportunity_queue.csv")

with queue_path.open(newline="") as f:
    rows = sorted(csv.DictReader(f), key=lambda row: float(row["priority_score"]), reverse=True)

print("Top CPG retail execution opportunities")
for row in rows[:10]:
    print(
        f"{row['retailer']} | {row['region']} | {row['category']} | {row['tier']} | "
        f"value=${float(row['opportunity_value']):,.0f} | "
        f"priority={float(row['priority_score']):.1f} | "
        f"ACV={float(row['avg_acv_distribution']):.1f}% | "
        f"OOS={float(row['avg_oos_rate']) * 100:.1f}% | "
        f"action={row['recommended_action']}"
    )
