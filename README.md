# Greenweez Finance & Campaign Analytics with dbt

This project is a portfolio-ready analytics engineering case study built with **dbt** and **BigQuery**. It demonstrates how raw e-commerce and paid marketing data can be transformed into clean, tested, and business-ready finance reporting models.

The pipeline starts with raw transactional and campaign data stored in BigQuery, then uses dbt to organize the transformation process into staging, intermediate, and mart layers. The first phase of the project focused on building the finance foundation from sales, product, and shipping data. In the next phase, campaign data from multiple advertising platforms was added to enrich the finance layer with marketing spend and ads-adjusted profitability metrics.

As a result, the system now enables a unified view of revenue, costs, operational margin, and advertising performance.

<img width="2034" height="378" alt="dbt dag" src="https://github.com/user-attachments/assets/2d8ef5a8-44dd-4c0a-a7c6-dea770697995" />

## Project Purpose

The goal of this project is to build a modular and production-oriented data pipeline that supports both **financial reporting** and **marketing performance analysis**.

This pipeline answers key business questions such as:

* How much revenue is generated daily and monthly?
* What is the purchase cost and margin?
* What is the operational margin after logistics costs?
* How much is spent on advertising?
* What is the impact of ad spend on profitability?

## Data Sources

### Operational Data

* `raw_gz_sales`
* `raw_gz_product`
* `raw_gz_ship`

### Marketing Data

* `raw_gz_adwords`
* `raw_gz_bing`
* `raw_gz_criterio`
* `raw_gz_facebook`

All data is stored in BigQuery and modeled using dbt.

## Data Transformation Architecture

The project follows a layered dbt architecture:

### 1. Staging Layer

In this layer, raw BigQuery data is cleaned and standardized.

Key transformations:

* column renaming
* data type casting
* schema alignment across sources

Campaign-specific transformations:

* `camPGN_name → campaign_name`
* `ads_cost (string → float64)`

Models:

* `stg_raw__sales`
* `stg_raw__product`
* `stg_raw__ship`
* `stg_raw_adwords`
* `stg_raw_bing`
* `stg_raw_criterio`
* `stg_raw_facebook`

### 2. Intermediate Layer

This layer contains reusable business logic.

Finance models:

* `int_sales_margin`
* `int_orders_margin`
* `int_orders_operational`

Campaign models:

* `int_campaigns` → unified campaign dataset
* `int_campaigns_day` → daily campaign aggregation

### 3. Mart Layer

Final reporting models used for analytics.

Core finance model:

* `finance_days`

Campaign-enriched models:

* `finance_campaigns_day`
* `finance_campaigns_month`

## Key Business Logic

### Finance Pipeline

From transactional data, the pipeline calculates:

* purchase cost
* margin
* operational margin
* average basket
* daily financial metrics

### Campaign Integration

Campaign data is integrated into the finance layer to calculate:

`ads_margin = operational_margin - ads_cost`

This enables analysis of profitability after marketing spend.

## Final Models

### finance_days

Daily finance reporting:

* revenue
* margin
* operational margin
* shipping & logistics costs

### finance_campaigns_day

Daily finance + campaign data:

* ads_cost
* ads_impression
* ads_clicks
* ads_margin
* revenue & margin metrics
*   
<img width="2150" height="904" alt="finance_view" src="https://github.com/user-attachments/assets/9c79ca45-c009-412e-80ab-23aef1de7d50" />

### finance_campaigns_month

Monthly aggregated reporting model for trend analysis.

<img width="1590" height="273" alt="bigquery" src="https://github.com/user-attachments/assets/0f6936f8-8e77-4314-a829-73f41d9b2748" />

## Data Quality

Tests implemented using dbt:

* `not_null`
* `unique`
* composite key tests

Ensures data consistency and reliability.

## Materialization Strategy

* staging → view
* intermediate → view
* mart → table
* `finance_campaigns_day` → view (override)

## Example dbt Commands

```bash
dbt parse
dbt build
```

Build only finance marts:

```bash
dbt build --select finance_campaigns_day finance_campaigns_month
```

Partial pipeline update example:

```bash
dbt build --select stg_raw_facebook+ --exclude finance_campaigns_month
```

## BigQuery Output

Final models are materialized in BigQuery and ready for:

* reporting
* dashboards
* validation queries

## Project Structure

```text
models/
├── staging/
├── intermediate/
└── mart/
    └── finance/
```

## Tech Stack

* dbt
* Google BigQuery
* dbt Cloud
* GitHub

## Portfolio Summary

This project demonstrates how I design and build an end-to-end analytics pipeline using dbt.

It started with a finance reporting system and was extended with campaign data integration to create a more realistic business use case.

The final result is a clean, modular, and production-ready data model that connects finance and marketing data for better decision-making.

