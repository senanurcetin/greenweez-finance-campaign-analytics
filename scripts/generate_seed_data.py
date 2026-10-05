"""Generate deterministic synthetic raw data for the DuckDB demo/CI targets.

Writes seeds/raw_gz_*.csv with the same column names as the real raw tables
(including quirks such as `pdt_id`, `purchse_PRICE`, `logCost`, `camPGN_name`
and `shipping_fee_1`). The data deliberately contains edge cases that the
models and tests are expected to handle:

  * orders without a shipping record          -> operational margin must not be NULL
  * a sold product missing from the product table -> relationships warning
  * days with ad spend but no orders          -> must stay visible in the daily mart
  * several ad platforms/campaigns on one day -> campaign union + daily rollup

Usage: python scripts/generate_seed_data.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED_DIR = Path(__file__).resolve().parent.parent / "seeds"
START = date(2023, 1, 1)
DAYS = 90
N_PRODUCTS = 30
MISSING_PRODUCT_ID = 1099          # sold, but absent from raw_gz_product
NO_ORDER_DAYS = {date(2023, 2, 14), date(2023, 3, 5)}
NO_SHIP_EVERY = 37                 # every 37th order has no shipping row

ADS = {
    # seed table -> (paid_source, key prefix, campaigns, daily cost scale)
    "adwords": ("adwords", "adw", ["Brand", "Generic", "Shopping"], 60.0),
    "bing": ("bing", "bng", ["Brand", "Generic"], 25.0),
    "criterio": ("criteo", "cri", ["Retargeting", "Prospecting"], 40.0),
    "facebook": ("facebook", "fbk", ["Lookalike", "Retargeting", "Spring Promo"], 45.0),
}


def write(name, header, rows):
    path = SEED_DIR / f"raw_gz_{name}.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} rows")


def main():
    rng = random.Random(42)
    SEED_DIR.mkdir(exist_ok=True)

    product_ids = [1000 + i for i in range(1, N_PRODUCTS + 1)]
    prices = {pid: round(rng.uniform(2.0, 40.0), 2) for pid in product_ids}
    prices[MISSING_PRODUCT_ID] = round(rng.uniform(5.0, 20.0), 2)  # used only for revenue
    write(
        "product",
        ["products_id", "purchse_PRICE"],
        [(pid, prices[pid]) for pid in product_ids],
    )

    sales, ship = [], []
    order_id = 100000
    for offset in range(DAYS):
        day = START + timedelta(days=offset)
        if day in NO_ORDER_DAYS:
            continue
        # mild weekly seasonality: more orders on weekends
        n_orders = rng.randint(9, 16) + (4 if day.weekday() >= 5 else 0)
        for _ in range(n_orders):
            order_id += 1
            n_lines = rng.randint(1, 4)
            pool = product_ids + ([MISSING_PRODUCT_ID] if order_id % 53 == 0 else [])
            products = rng.sample(pool, n_lines)
            if order_id % 53 == 0 and MISSING_PRODUCT_ID not in products:
                products[0] = MISSING_PRODUCT_ID
            order_revenue = 0.0
            for pid in products:
                qty = rng.randint(1, 5)
                revenue = round(qty * prices[pid] * rng.uniform(1.25, 1.7), 2)
                order_revenue += revenue
                sales.append((day.isoformat(), order_id, pid, revenue, qty))
            if order_id % NO_SHIP_EVERY == 0:
                continue  # edge case: no shipping record
            fee = round(rng.choice([0.0, 4.9, 5.9, 7.9]) if order_revenue < 80 else 0.0, 2)
            ship.append(
                (
                    order_id,
                    fee,
                    fee,
                    round(rng.uniform(1.0, 4.0), 2),   # logCost
                    round(rng.uniform(2.0, 6.5), 2),   # ship_cost
                )
            )
    write("sales", ["date_date", "orders_id", "pdt_id", "revenue", "quantity"], sales)
    write("ship", ["orders_id", "shipping_fee", "shipping_fee_1", "logCost", "ship_cost"], ship)

    for table, (source, prefix, campaigns, scale) in ADS.items():
        rows = []
        for offset in range(DAYS):
            day = START + timedelta(days=offset)
            for idx, campaign in enumerate(campaigns, start=1):
                impressions = int(rng.uniform(800, 6000) * scale / 40)
                clicks = int(impressions * rng.uniform(0.01, 0.06))
                cost = round(clicks * rng.uniform(0.06, 0.32), 2)
                rows.append(
                    (day.isoformat(), source, f"{prefix}_{idx:02d}",
                     f"{campaign}", cost, impressions, clicks)
                )
        write(
            table,
            ["date_date", "paid_source", "campaign_key", "camPGN_name", "ads_cost", "impression", "click"],
            rows,
        )


if __name__ == "__main__":
    main()
