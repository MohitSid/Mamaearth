import pandas as pd
import numpy as np

customers = pd.read_csv(r"C:\Users\hp\Downloads\customers.csv")
products = pd.read_csv(r"C:\Users\hp\Downloads\products.csv")
orders = pd.read_csv(r"C:\Users\hp\Downloads\orders.csv")

print("Customers: ", customers.shape)
print("Products: ", products.shape)
print("Orders: ", orders.shape)

display(orders.head())
display(orders.info())

orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

print(orders["payment_method"].nunique())
print(orders["payment_method"].value_counts())


natural_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

# Identify duplicate rows before removing them
duplicate_mask = orders.duplicated(
    subset=natural_key,
    keep="first"
)

# Print the IDs that will be removed
print("Duplicate order IDs:")
print(orders.loc[duplicate_mask, "order_id"].tolist())

# Create a cleaned copy
orders_clean = orders.loc[~duplicate_mask].copy()

print("Shape after removing duplicates:", orders_clean.shape)

# Count missing values before imputation
print(
    orders_clean[["discount_pct", "rating"]]
    .isna()
    .sum()
)

# Calculate median before filling missing ratings
rating_median = orders_clean["rating"].median()
print("Rating median:", rating_median)

# Impute missing values
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

orders_clean["rating"] = (
    orders_clean["rating"].fillna(rating_median)
)

# Verify
print(
    orders_clean[["discount_pct", "rating"]]
    .isna()
    .sum()
)


# Merge cleaned orders with products
merged = orders_clean.merge(
    products,
    on="product_id",
    how="left",
    validate="many_to_one"
)

# Merge with customers
merged = merged.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one"
)

# Calculate order value after discount
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

print("Merged shape:", merged.shape)
print("Total order value:", round(merged["order_value"].sum(), 2))
print("Missing merged values:")
print(merged[["price", "city", "city_tier"]].isna().sum())


# Independently calculate the value of the five dropped duplicate rows
dropped_duplicates = orders.loc[
    orders.duplicated(subset=natural_key, keep="first")
].copy()

dropped_merged = dropped_duplicates.merge(
    products[["product_id", "price"]],
    on="product_id",
    how="left"
)

dropped_merged["order_value"] = (
    dropped_merged["quantity"]
    * dropped_merged["price"]
    * (1 - dropped_merged["discount_pct"].fillna(0) / 100)
)

print("Dropped duplicate rows:", len(dropped_duplicates))
print(
    "Revenue attributable to dropped duplicates:",
    round(dropped_merged["order_value"].sum(), 2)
)
print(
    "Revenue after deduplication:",
    round(merged["order_value"].sum(), 2)
)

# Task 6 — IQR outlier detection on quantity
# Calculate quartiles and IQR
Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower)
print("Upper bound:", upper)

# Flag outliers without dropping rows
merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)

outliers = merged.loc[
    merged["is_outlier"],
    ["order_id", "quantity"]
]

print("\nOutlier orders:")
print(outliers.to_string(index=False))
print("\nNumber of outliers:", merged["is_outlier"].sum())


# Task 7 — Hypothesis: does COD have a higher return rate?
# Calculate order counts and return rates
payment_returns = (
    merged.groupby("payment_method")["returned"]
    .agg(
        count="count",
        mean="mean"
    )
)

payment_returns["return_rate_pct"] = (
    payment_returns["mean"] * 100
).round(1)

print(payment_returns)


cod_rate = payment_returns.loc["COD", "return_rate_pct"]
card_rate = payment_returns.loc["CARD", "return_rate_pct"]
upi_rate = payment_returns.loc["UPI", "return_rate_pct"]

print("\nHypothesis: COD orders have a higher return rate.")
print(f"COD return rate: {cod_rate}%")
print(f"CARD return rate: {card_rate}%")
print(f"UPI return rate: {upi_rate}%")

if cod_rate > max(card_rate, upi_rate):
    print("Conclusion: Confirmed — COD has the highest observed return rate.")
else:
    print("Conclusion: Not confirmed.")

# Task 8 — Multi-level segmentation
# Segment by payment method and city tier
segment_returns = (
    merged.groupby(["payment_method", "city_tier"])["returned"]
    .agg(
        order_count="count",
        returned_orders="sum",
        return_rate="mean"
    )
    .reset_index()
)

segment_returns["return_rate_pct"] = (
    segment_returns["return_rate"] * 100
).round(1)

segment_returns = segment_returns.sort_values(
    "return_rate_pct",
    ascending=False
)

print(segment_returns.to_string(index=False))

# Explicitly identify the highest-risk segment
highest_risk = segment_returns.iloc[0]

print("\nHighest-risk segment:")
print(
    f"{highest_risk['payment_method']} + "
    f"Tier-{highest_risk['city_tier']}: "
    f"{highest_risk['return_rate_pct']}% return rate "
    f"({highest_risk['returned_orders']:.0f} returns "
    f"out of {highest_risk['order_count']:.0f} orders)"
)

# Task 9 — Correlation analysis
# Calculate correlation matrix
corr_cols = [
    "rating",
    "returned",
    "discount_pct",
    "quantity"
]

corr_matrix = merged[corr_cols].corr()

print("Correlation matrix:")
print(corr_matrix.round(2))


def correlation_band(r):
    strength = abs(r)

    if strength < 0.20:
        return "negligible"
    elif strength < 0.40:
        return "weak"
    elif strength < 0.70:
        return "moderate"
    else:
        return "strong"


pairs = [
    ("rating", "returned"),
    ("rating", "discount_pct"),
    ("rating", "quantity"),
    ("returned", "discount_pct"),
    ("returned", "quantity"),
    ("discount_pct", "quantity")
]

print("\nPairwise correlation interpretation:")

for col1, col2 in pairs:
    r = corr_matrix.loc[col1, col2]
    print(
        f"{col1} vs {col2}: "
        f"r = {r:.2f}, "
        f"{correlation_band(r)} correlation"
    )

discount_return_corr = corr_matrix.loc["discount_pct", "returned"]

print("\nHypothesis: Higher discounts reduce returns.")
print(
    f"discount_pct vs returned: r = {discount_return_corr:.2f}"
)

if discount_return_corr < 0:
    print("Direction: Negative association, as hypothesized.")
else:
    print("Direction: Not negative; the hypothesis is not supported by direction.")

# Task 10:  Outlier-corrected time series
# Ensure dates and revenue values are ready
merged["order_date"] = pd.to_datetime(merged["order_date"])
merged["year_month"] = merged["order_date"].dt.to_period("M")

# Revenue including outliers
monthly_revenue_all = (
    merged.groupby("year_month")["order_value"].sum().round(2)
)

# Revenue excluding quantity outliers
monthly_revenue_corrected = (
    merged.loc[merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
    .round(2)
)

print("Including outliers:")
print(monthly_revenue_all)

print("\nCorrected revenue:")
print(monthly_revenue_corrected)

if abs(discount_return_corr) < 0.20:
    print("Strength: Negligible association; the hypothesis is not meaningfully supported.")


