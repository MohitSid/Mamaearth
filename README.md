# Mamaearth
# Mamaearth Growth Analytics Pipeline

## Project Overview

This project analyzes Mamaearth's order data to identify revenue patterns, payment-method return rates, high-risk customer segments, duplicate-order impact, and monthly revenue trends.

The project contains three connected layers:

1. **SQL Relational Layer:** Creates and populates relational tables and generates business reports.
2. **Python/Pandas Analysis Layer:** Cleans raw CSV data, removes duplicates, handles missing values, detects outliers, performs EDA, and generates visualizations.
3. **GenAI Narrative Layer:** Converts verified analytical findings into a Situation–Complication–Resolution (SCR) business narrative using Gemini, with a deterministic offline fallback.

All numerical findings are calculated from the supplied data rather than manually estimated.

## Repository Structure

```text
.
├── README.md
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    └── generate_narrative.py
```

## Requirements

- Python 3.10 or a compatible version
- MySQL or another SQL engine compatible with the supplied SQL syntax
- Python packages: `pandas`, `matplotlib`, and `google-genai`
- A Gemini API key for online narrative generation; optional for offline mode

Install the required packages:

```bash
pip install pandas matplotlib google-genai
```

Install any additional packages imported by the project scripts.

## Execution Order

### Step 1 — SQL Relational Layer

Execute the SQL files in the following order using your SQL client:

1. `sql/schema.sql` — creates the `customers`, `products`, and `orders` tables with primary and foreign keys.
2. `sql/seed_data.sql` — loads the supplied CSV data into the relational tables.
3. `sql/reports.sql` — runs the required reporting queries, including revenue calculations, return-rate analysis, customer segmentation, ranking, and joins.

Verify the query results against the expected outputs in the assignment.

### Step 2 — Python/Pandas Analysis Layer

From the repository root, run:

```bash
python analysis/clean_and_eda.py
```

This script reads the original CSV files directly and performs:

- Data inspection and payment-method standardization
- Duplicate-order detection and removal
- Missing-value imputation
- Revenue reconciliation
- IQR-based quantity outlier detection
- Return-rate and customer-segment analysis
- Correlation and monthly revenue analysis
- Export of verified results to `narrator/findings.json`

The Pandas pipeline is independent of the SQL database and uses the original CSV files as its source.

### Step 3 — Generate Visualizations

Run:

```bash
python analysis/visualize.py
```

The script regenerates the following charts:

- `visualizations/return_rate_by_payment.png` — return rates by payment method.
- `visualizations/monthly_revenue_trend.png` — monthly revenue trend after excluding the identified quantity outliers.

Both charts are generated from the source CSV data using the cleaning and calculation rules defined in the project.

### Step 4 — GenAI-Powered Business Narrative

The narrative layer reads `narrator/findings.json` and generates a business report using the Situation–Complication–Resolution (SCR) structure.

When Gemini is configured and available, the online generator produces the narrative using the verified findings. If the API key is missing or the API request fails, a deterministic offline fallback generates the narrative without requiring a network connection or API quota.

For online generation, configure the `GEMINI_API_KEY` environment variable. Never commit API keys or other secrets to GitHub.

The narrative output and validation results should be generated from the current findings rather than manually edited.

## Data Validation and Reconciliation

The project checks the following key figures against the generated narrative:

- Cleaned total revenue
- COD return rate
- COD and City Tier 2 return rate
- Duplicate-reconciliation difference
- Corrected peak month and its revenue

A numeric accuracy checker verifies that all five required figures appear in the narrative, allowing for equivalent number formatting.

The SQL and Pandas outputs must be reconciled using the definitions specified in the assignment. All results should be reproducible from the supplied source data.

## Reproducibility

Run the stages in the documented order and keep the original CSV files unchanged. Regenerate the analysis results, findings JSON, visualizations, and narrative whenever the source data or processing logic changes.

The pipeline is designed to support both online GenAI generation and offline narrative generation, ensuring that the final report does not depend entirely on API availability.
