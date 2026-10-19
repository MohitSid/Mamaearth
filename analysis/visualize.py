# Task 11: (i). return_rate_by_payment.png - a bar chart of return rate by payment method, descending with the exact percentage labeled on each bar, and a title that states the findings
          #(ii). monthly_revenue_trend.png - a line chart of the outlier-corrected monthly revenue from task 10, with axis label and title naming the actual peak month  
# analysis/visualize.py

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Resolve paths relative to the repository root
ROOT = Path.cwd()
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("Project root:", ROOT)
print("Data folder exists:", DATA_DIR.exists())

# --------------------------------------------------
# 1. Load the original CSVs
# --------------------------------------------------
customers = pd.read_csv(DATA_DIR /r"C:\Users\hp\Downloads\customers.csv")
products = pd.read_csv(DATA_DIR / r"C:\Users\hp\Downloads\products.csv")
orders = pd.read_csv(DATA_DIR /r"C:\Users\hp\Downloads\orders.csv")

# --------------------------------------------------
# 2. Standardize payment methods
# --------------------------------------------------
orders["payment_method"] = (
    orders["payment_method"].str.strip().str.upper()
)

# --------------------------------------------------
# 3. Remove duplicate orders
# --------------------------------------------------
natural_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned",
]

orders_clean = orders.drop_duplicates(
    subset=natural_key,
    keep="first"
).copy()

# --------------------------------------------------
# 4. Impute missing values
# --------------------------------------------------
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

orders_clean["rating"] = (
    orders_clean["rating"].fillna(
        orders_clean["rating"].median()
    )
)

# --------------------------------------------------
# 5. Merge and calculate order value
# --------------------------------------------------
merged = orders_clean.merge(
    products,
    on="product_id",
    how="left",
    validate="many_to_one"
)

merged = merged.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one"
)

merged["order_date"] = pd.to_datetime(
    merged["order_date"]
)

merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

# --------------------------------------------------
# 6. Flag quantity outliers using IQR
# --------------------------------------------------
q1 = merged["quantity"].quantile(0.25)
q3 = merged["quantity"].quantile(0.75)
iqr = q3 - q1

lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)

print("Merged rows:", len(merged))
print("Quantity outliers:", int(merged["is_outlier"].sum()))

# --------------------------------------------------
# 7. Visualization 1: Return rate by payment method
# --------------------------------------------------
return_rates = (
    merged.groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("\nReturn rates (%):")
print(return_rates.round(1))

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    return_rates.index,
    return_rates.values
)

ax.set_title(
    "COD Returns at 44.4% — 3x Card"
)
ax.set_xlabel("Payment method")
ax.set_ylabel("Return rate (%)")
ax.set_ylim(0, max(return_rates.values) * 1.2)

ax.bar_label(
    bars,
    labels=[f"{v:.1f}%" for v in return_rates.values],
    padding=3
)

fig.tight_layout()
fig.savefig(
    OUTPUT_DIR / "return_rate_by_payment.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close(fig)

# --------------------------------------------------
# 8. Visualization 2: Corrected monthly revenue
# --------------------------------------------------
merged["year_month"] = (
    merged["order_date"].dt.to_period("M")
)

# Exclude outlier orders from the revenue trend only
corrected = merged.loc[~merged["is_outlier"]]

monthly_revenue = (
    corrected.groupby("year_month")["order_value"]
    .sum()
    .sort_index()
)

print("\nOutlier-corrected monthly revenue:")
print(monthly_revenue.round(2))

peak_month = monthly_revenue.idxmax()

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    monthly_revenue.index.astype(str),
    monthly_revenue.values,
    marker="o"
)

ax.set_title(
    f"Monthly Revenue — Outlier-Corrected "
    f"(Peak: {peak_month})"
)
ax.set_xlabel("Order month")
ax.set_ylabel("Revenue")
ax.tick_params(axis="x", rotation=45)

fig.tight_layout()
fig.savefig(
    OUTPUT_DIR / "monthly_revenue_trend.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close(fig)

print("\nSaved visualizations:")
print(OUTPUT_DIR / "return_rate_by_payment.png")
print(OUTPUT_DIR / "monthly_revenue_trend.png")
