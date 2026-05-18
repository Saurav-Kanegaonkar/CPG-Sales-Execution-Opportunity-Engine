-- Snowflake-style retail execution validation checks
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
