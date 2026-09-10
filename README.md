# Ecommerce Sales & Customer Analytics

## RFM-Based Customer Segmentation and Churn Risk Analysis

A data analytics project focused on understanding e-commerce sales performance, customer purchasing behavior, customer value, and churn risk using transactional retail data. The project applies RFM (Recency, Frequency, Monetary) analysis to segment customers and develop targeted, data-driven marketing strategies.

---

## Project Overview

Customer retention and customer lifetime value are critical factors in e-commerce. This project analyzes transactional retail data to identify valuable customers, understand purchasing patterns, detect customers at risk of churn, and recommend appropriate marketing strategies for different customer segments.

The analysis combines:

- InvoiceNo
- StockCode
- Description
- InvoiceDate
- UnitPrice
- CustomerID
- Country
---

## Business Objectives

The primary objectives of this project are to:

1. Analyze overall e-commerce sales performance.
2. Understand customer purchasing behavior.
3. Identify high-value and loyal customers.
4. Quantity purchase by each costumer
---

## Dataset

The project uses the Online Retail transactional dataset.

### Dataset Features

| Column | Description |
|---|---|
| `InvoiceNo` | Unique invoice number |
| `StockCode` | Product identification code |
| `Description` | Product description |
| `Quantity` | Number of products purchased |
| `InvoiceDate` | Date and time of transaction |
| `UnitPrice` | Price per unit |
| `CustomerID` | Unique customer identifier |
| `Country` | Customer's country |

---

## Data Preparation

The dataset is first examined for data quality issues, including:

- Missing values
- Duplicate records
- Cancelled invoices
- Zero unit prices
- Negative unit prices
- Invalid transactions

For customer-level analysis, cancelled and invalid sales transactions are excluded.


## Exploratory Data Analysis

The Exploratory Data Analysis (EDA) phase focuses on understanding overall sales performance, customer behavior, product performance, and purchasing patterns within the e-commerce dataset.

The analysis covers the following key business metrics:

- **Number of Orders** – Determines the total number of unique orders.
- **Number of Customers** – Identifies the number of unique customers.
- **Number of Products** – Measures the number of unique products available in the dataset.
- **Average Order Value (AOV)** – Calculates the average revenue generated per order.
- **Monthly Revenue Trends** – Analyzes revenue performance across different months to identify growth patterns and seasonal trends.
- **Country-wise Revenue** – Compares sales performance across different countries.
- **Product Performance** – Identifies top-performing products based on sales and purchasing activity.
- **Customer Purchasing Behavior** – Examines customer order frequency, spending patterns, and overall purchasing activity.

These analyses provide the foundation for the subsequent **RFM-based customer segmentation and churn risk analysis**.

## Key Business Insights

The analysis provides actionable insights that can support data-driven business and marketing decisions. Key outcomes include:

- **Identify High-Value Customers** – Recognize customers who contribute significantly to overall revenue.
- **Understand Customer Purchasing Behavior** – Analyze customer purchase frequency, spending patterns, and engagement levels.
- **Improve Customer Retention** – Develop targeted strategies to retain valuable and loyal customers.
- **Detect Potential Churn** – Identify inactive or at-risk customers before they are completely lost.
- **Prioritize High-Value At-Risk Customers** – Focus retention efforts on customers who have both high customer value and elevated churn risk.
- **Personalize Marketing Strategies** – Create segment-specific campaigns based on customer behavior and RFM characteristics.
- **Increase Repeat Purchases** – Encourage customers to purchase more frequently through targeted offers and loyalty initiatives.
- **Optimize Marketing Resource Allocation** – Direct marketing efforts and budgets toward customer segments with the highest potential business impact.

These insights enable the business to move from **descriptive sales analysis to actionable customer-focused decision-making**.
Tools & Technologies

##The project was developed using:

- Python
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- Microsoft Excel

## Conclusion

The quantity analysis provides valuable insights into the purchasing behavior and transaction patterns of the e-commerce business. The dataset contains both positive and negative quantities, indicating regular sales as well as returned or cancelled transactions.

The analysis shows that most transactions involve positive quantities, while negative quantity records represent a smaller portion of the overall transactions. However, the presence of extreme quantity values indicates that some transactions may require further investigation for potential bulk purchases, returns, or data anomalies.

Overall, quantity-based analysis helps the business:

- Understand product purchasing volumes.
- Identify high-volume transactions.
- Monitor returned or cancelled quantities.
- Detect unusual or extreme transaction quantities.
- Evaluate customer purchasing patterns.
- Support inventory and stock management decisions.

By combining quantity analysis with sales, customer, and RFM analysis, the business can gain a more comprehensive understanding of purchasing behavior and make better data-driven decisions.
