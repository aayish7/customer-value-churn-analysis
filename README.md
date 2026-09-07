# ecommerce-sales-customer-analytics-
RFM-based customer segmentation and churn risk analysis for an e-commerce business, with data-driven marketing recommendations per segment.
# ============================================================
# E-COMMERCE CUSTOMER ANALYTICS
# RFM CUSTOMER SEGMENTATION + CHURN RISK ANALYSIS
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

FILE_PATH = "ecommerce_data.csv"

df = pd.read_csv(FILE_PATH)

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())


# ------------------------------------------------------------
# 2. DATA CLEANING
# ------------------------------------------------------------

# Remove duplicate records
df = df.drop_duplicates()

# Convert date column
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

# Remove rows with missing essential values
df = df.dropna(
    subset=["CustomerID", "InvoiceDate", "Quantity", "UnitPrice"]
)

# Remove invalid transactions
df = df[df["Quantity"] > 0]
df = df[df["UnitPrice"] > 0]

# Customer ID as string
df["CustomerID"] = df["CustomerID"].astype(str)

# Calculate transaction revenue
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

print("\nCleaned dataset shape:", df.shape)


# ------------------------------------------------------------
# 3. BASIC BUSINESS ANALYTICS
# ------------------------------------------------------------

total_revenue = df["Revenue"].sum()
total_customers = df["CustomerID"].nunique()
total_orders = df["InvoiceNo"].nunique()

print("\n========== BUSINESS KPIs ==========")
print(f"Total Revenue : ${total_revenue:,.2f}")
print(f"Customers     : {total_customers:,}")
print(f"Orders        : {total_orders:,}")
print(f"Average Order : ${total_revenue / total_orders:,.2f}")


# ------------------------------------------------------------
# 4. CREATE RFM DATASET
# ------------------------------------------------------------

# Analysis date = one day after the last transaction
analysis_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

print("\nAnalysis date:", analysis_date)

rfm = df.groupby("CustomerID").agg({

    "InvoiceDate": lambda x:
        (analysis_date - x.max()).days,

    "InvoiceNo": "nunique",

    "Revenue": "sum"

})

# Rename columns
rfm.columns = [
    "Recency",
    "Frequency",
    "Monetary"
]

print("\n========== RFM DATA ==========")
print(rfm.head())


# ------------------------------------------------------------
# 5. RFM SCORE CALCULATION
# ------------------------------------------------------------

# Recency:
# Lower is better, therefore reverse scoring.

rfm["R_Score"] = pd.qcut(
    rfm["Recency"],
    q=5,
    labels=[5, 4, 3, 2, 1],
    duplicates="drop"
).astype(int)

# Frequency:
# Higher is better.

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Monetary:
# Higher is better.

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Combined RFM score
rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str)
    + rfm["F_Score"].astype(str)
    + rfm["M_Score"].astype(str)
)

rfm["RFM_Total"] = (
    rfm["R_Score"]
    + rfm["F_Score"]
    + rfm["M_Score"]
)

print("\n========== RFM SCORES ==========")
print(rfm.head())


# ------------------------------------------------------------
# 6. CUSTOMER SEGMENTATION
# ------------------------------------------------------------

def assign_segment(row):

    R = row["R_Score"]
    F = row["F_Score"]
    M = row["M_Score"]

    # Champions
    if R >= 4 and F >= 4 and M >= 4:
        return "Champions"

    # Loyal Customers
    elif R >= 3 and F >= 4:
        return "Loyal Customers"

    # Potential Loyalists
    elif R >= 4 and F >= 2:
        return "Potential Loyalists"

    # Big Spenders
    elif M >= 4:
        return "Big Spenders"

    # New Customers
    elif R >= 4 and F <= 2:
        return "New Customers"

    # At Risk
    elif R <= 2 and F >= 3:
        return "At Risk"

    # Cannot Lose Them
    elif R <= 2 and F >= 4 and M >= 4:
        return "Cannot Lose Them"

    # Hibernating
    elif R <= 2 and F <= 2:
        return "Hibernating"

    else:
        return "Needs Attention"


rfm["Segment"] = rfm.apply(assign_segment, axis=1)

print("\n========== CUSTOMER SEGMENTS ==========")
print(rfm["Segment"].value_counts())


# ------------------------------------------------------------
# 7. CHURN RISK ANALYSIS
# ------------------------------------------------------------

# Churn definition:
# Customers who have not purchased for 90+ days
# are considered at risk of churn.

def churn_risk(recency):

    if recency >= 180:
        return "High Risk"

    elif recency >= 90:
        return "Medium Risk"

    else:
        return "Low Risk"


rfm["Churn_Risk"] = rfm["Recency"].apply(churn_risk)


print("\n========== CHURN RISK ==========")
print(rfm["Churn_Risk"].value_counts())


# ------------------------------------------------------------
# 8. CHURN PROBABILITY SCORE
# ------------------------------------------------------------

# Create a simple business-oriented churn probability.

rfm["Churn_Probability"] = np.where(
    rfm["Recency"] >= 180,
    0.90,
    np.where(
        rfm["Recency"] >= 90,
        0.60,
        0.20
    )
)

rfm["Churn_Probability"] = (
    rfm["Churn_Probability"] * 100
).round(1)

print("\nChurn probability:")
print(
    rfm[
        [
            "Recency",
            "Segment",
            "Churn_Risk",
            "Churn_Probability"
        ]
    ].head(10)
)


# ------------------------------------------------------------
# 9. MARKETING RECOMMENDATIONS
# ------------------------------------------------------------

marketing_actions = {

    "Champions":
        "VIP rewards, early access, exclusive products, referral programs",

    "Loyal Customers":
        "Loyalty points, personalized offers, subscription programs",

    "Potential Loyalists":
        "Cross-selling, product recommendations, limited-time discounts",

    "Big Spenders":
        "Premium products, VIP service, high-value bundles",

    "New Customers":
        "Welcome campaign, onboarding emails, first-repeat purchase discount",

    "At Risk":
        "Win-back campaign, personalized discount, reminder emails",

    "Cannot Lose Them":
        "Dedicated retention campaign, high-value incentive, personal outreach",

    "Hibernating":
        "Reactivation campaign, strong discount, new-product recommendations",

    "Needs Attention":
        "Personalized recommendations and targeted promotional campaigns"
}


rfm["Marketing_Recommendation"] = (
    rfm["Segment"].map(marketing_actions)
)


# ------------------------------------------------------------
# 10. CUSTOMER ANALYTICS REPORT
# ------------------------------------------------------------

segment_report = rfm.groupby("Segment").agg(

    Customers=("Segment", "count"),

    Avg_Recency=("Recency", "mean"),

    Avg_Frequency=("Frequency", "mean"),

    Avg_Monetary=("Monetary", "mean"),

    Total_Revenue=("Monetary", "sum"),

    Avg_Churn_Probability=("Churn_Probability", "mean")

).reset_index()


segment_report["Revenue_Percentage"] = (
    segment_report["Total_Revenue"]
    / segment_report["Total_Revenue"].sum()
    * 100
)


segment_report = segment_report.sort_values(
    "Total_Revenue",
    ascending=False
)


print("\n========== SEGMENT REPORT ==========")
print(segment_report)


# ------------------------------------------------------------
# 11. VISUALIZATION - CUSTOMER SEGMENTS
# ------------------------------------------------------------

plt.figure(figsize=(12, 6))

sns.countplot(
    data=rfm,
    y="Segment",
    order=rfm["Segment"].value_counts().index,
    palette="viridis"
)

plt.title("Customer Distribution by Segment")
plt.xlabel("Number of Customers")
plt.ylabel("Customer Segment")

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 12. VISUALIZATION - CHURN RISK
# ------------------------------------------------------------

plt.figure(figsize=(8, 6))

churn_counts = rfm["Churn_Risk"].value_counts()

sns.barplot(
    x=churn_counts.index,
    y=churn_counts.values,
    palette="rocket"
)

plt.title("Customer Churn Risk Distribution")
plt.xlabel("Churn Risk")
plt.ylabel("Number of Customers")

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 13. VISUALIZATION - REVENUE BY SEGMENT
# ------------------------------------------------------------

plt.figure(figsize=(12, 6))

revenue_data = segment_report.sort_values(
    "Total_Revenue",
    ascending=True
)

plt.barh(
    revenue_data["Segment"],
    revenue_data["Total_Revenue"],
    color="steelblue"
)

plt.title("Revenue Contribution by Customer Segment")
plt.xlabel("Revenue")
plt.ylabel("Customer Segment")

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 14. RFM HEATMAP
# ------------------------------------------------------------

rfm_heatmap = rfm.groupby("Segment")[
    ["Recency", "Frequency", "Monetary"]
].mean()

plt.figure(figsize=(10, 7))

sns.heatmap(
    rfm_heatmap,
    annot=True,
    fmt=".1f",
    cmap="YlGnBu"
)

plt.title("Average RFM Metrics by Customer Segment")

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 15. TOP CUSTOMERS
# ------------------------------------------------------------

top_customers = rfm.sort_values(
    "Monetary",
    ascending=False
).head(20)

print("\n========== TOP 20 CUSTOMERS ==========")

print(
    top_customers[
        [
            "Recency",
            "Frequency",
            "Monetary",
            "Segment",
            "Churn_Risk"
        ]
    ]
)


# ------------------------------------------------------------
# 16. HIGH-VALUE CUSTOMERS AT RISK
# ------------------------------------------------------------

high_value_risk = rfm[
    (rfm["Monetary"] >= rfm["Monetary"].quantile(0.75))
    &
    (rfm["Churn_Risk"].isin(["Medium Risk", "High Risk"]))
]

high_value_risk = high_value_risk.sort_values(
    "Monetary",
    ascending=False
)

print("\n========== HIGH-VALUE CUSTOMERS AT RISK ==========")

print(
    high_value_risk[
        [
            "Recency",
            "Frequency",
            "Monetary",
            "Segment",
            "Churn_Risk",
            "Churn_Probability",
            "Marketing_Recommendation"
        ]
    ].head(20)
)


# ------------------------------------------------------------
# 17. OPTIONAL MACHINE LEARNING CHURN MODEL
# ------------------------------------------------------------

# Create binary churn target
# 1 = churn risk
# 0 = active customer

rfm["Churn"] = np.where(
    rfm["Recency"] >= 90,
    1,
    0
)


features = [
    "Recency",
    "Frequency",
    "Monetary"
]

X = rfm[features]
y = rfm["Churn"]


# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Feature scaling
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# Random Forest
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(
    X_train_scaled,
    y_train
)


# Predictions
y_pred = model.predict(X_test_scaled)


print("\n========== CHURN MODEL ==========")

print(
    classification_report(
        y_test,
        y_pred
    )
)


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ------------------------------------------------------------
# 18. FEATURE IMPORTANCE
# ------------------------------------------------------------

importance = pd.DataFrame({

    "Feature": features,

    "Importance": model.feature_importances_

}).sort_values(
    "Importance",
    ascending=False
)


print("\n========== CHURN FEATURE IMPORTANCE ==========")

print(importance)


plt.figure(figsize=(8, 5))

sns.barplot(
    data=importance,
    x="Importance",
    y="Feature",
    palette="Blues_r"
)

plt.title("Factors Influencing Churn")

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 19. SAVE CUSTOMER ANALYTICS
# ------------------------------------------------------------

rfm.to_csv(
    "customer_rfm_segmentation.csv"
)

segment_report.to_csv(
    "customer_segment_report.csv",
    index=False
)

high_value_risk.to_csv(
    "high_value_customers_at_risk.csv"
)

print("\nFiles created successfully:")
print("1. customer_rfm_segmentation.csv")
print("2. customer_segment_report.csv")
print("3. high_value_customers_at_risk.csv")


# ------------------------------------------------------------
# 20. FINAL BUSINESS SUMMARY
# ------------------------------------------------------------

print("\n==========================================")
print("          FINAL BUSINESS SUMMARY")
print("==========================================")

print(
    f"Total Customers: {len(rfm):,}"
)

print(
    f"Total Revenue: ${rfm['Monetary'].sum():,.2f}"
)

print(
    f"High Churn Risk Customers: "
    f"{(rfm['Churn_Risk'] == 'High Risk').sum():,}"
)

print(
    f"Medium Churn Risk Customers: "
    f"{(rfm['Churn_Risk'] == 'Medium Risk').sum():,}"
)

print(
    f"Low Churn Risk Customers: "
    f"{(rfm['Churn_Risk'] == 'Low Risk').sum():,}"
)

print("\nTop Customer Segment by Revenue:")

print(
    segment_report.iloc[0]["Segment"]
)

print("\nRecommended marketing strategies:")

for segment, action in marketing_actions.items():

    print(f"\n{segment}:")
    print(f"  -> {action}")
