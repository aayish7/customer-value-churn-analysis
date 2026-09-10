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

Sales value is calculated using:

```text
Sales = Quantity × UnitPrice
