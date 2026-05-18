# Data Dictionary

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
