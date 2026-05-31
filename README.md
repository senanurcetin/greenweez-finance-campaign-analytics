# Greenweez Finance and Campaign Analytics

Archive proof for dbt-based finance modeling, campaign integration, and BigQuery reporting design.

## Why this project exists

This repository shows how transactional finance data and paid campaign data can be modeled together so teams can analyze margin, logistics costs, and advertising impact from one reporting layer.

## Portfolio role

`archive proof`

## Business framing

The project is designed to answer questions such as:

- How much operational margin is generated after logistics costs?
- How does ad spend affect daily and monthly profitability?
- What reporting models are needed to connect revenue, cost, and campaign performance cleanly?

## Architecture snapshot

- **Warehouse target:** BigQuery
- **Transformation layer:** dbt
- **Model structure:** staging, intermediate, and marts
- **Output focus:** finance reporting with campaign-enriched profitability views
- **Project scope:** analytics engineering and reporting design rather than application delivery

## Core reporting models

- `finance_days`
- `finance_campaigns_day`
- `finance_campaigns_month`
- `int_orders_margin`
- `int_campaigns_day`

## What this proves

- You can build layered dbt projects for finance and marketing analytics.
- You can define reusable intermediate logic before exposing mart-level reporting models.
- You can frame analytics work in business terms such as margin and ad-adjusted profitability.

## Local setup

```bash
python -m pip install dbt-duckdb
dbt deps --profiles-dir .github/dbt-profiles
dbt parse --profiles-dir .github/dbt-profiles
```

## Quality checks

The GitHub Actions workflow runs:

```bash
dbt deps --profiles-dir .github/dbt-profiles
dbt parse --profiles-dir .github/dbt-profiles
```

## Limitations

- This repo emphasizes warehouse modeling, not dashboard UX.
- It is a supporting analytics project, not a lead industrial case study.
- Campaign performance should be read as reporting logic, not production marketing attribution infrastructure.

## License

MIT
