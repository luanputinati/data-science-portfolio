# Customer and E-commerce Insights

Exploratory data analysis and data visualization project using two prepared datasets: a customer profile dataset and an e-commerce product dataset.

The project applies concepts from previous data collection, cleaning and preparation modules to generate visual insights with Python, Pandas, Matplotlib and Seaborn.

---

## Project Objective

The objective of this project is to explore demographic, professional and commercial patterns through statistical summaries and data visualizations.

The analysis is divided into two independent sections:

1. **Customer Analysis**
   - demographic characteristics;
   - salary distribution;
   - professional experience;
   - education level;
   - professional area;
   - numerical correlations.

2. **E-commerce Analysis**
   - product price distribution;
   - product distribution by brand;
   - estimated sales by brand;
   - reviews and estimated sales;
   - discounts and estimated sales;
   - rating and price;
   - numerical correlations.

The datasets are analyzed separately because they do not share a common identifier that would allow a reliable merge between customers and products.

---

## Project Structure

```text
04-Data-Visualization/
├── data/
│   ├── clientes_preparados.csv
│   └── ecommerce_preparados.csv
│
├── notebooks/
│   └── customer_ecommerce_insights.ipynb
│
├── reports/
│   ├── figures/
│   │   ├── customer_age_distribution.png
│   │   ├── customer_correlation_heatmap.png
│   │   ├── customer_salary_distribution.png
│   │   ├── discount_sales_relationship.png
│   │   ├── ecommerce_correlation_heatmap.png
│   │   ├── experience_salary_relationship.png
│   │   ├── median_salary_by_professional_area.png
│   │   ├── product_price_distribution.png
│   │   ├── rating_price_relationship.png
│   │   ├── reviews_estimated_sales_relationship.png
│   │   ├── salary_by_education_level.png
│   │   ├── top_brands_by_estimated_sales.png
│   │   └── top_brands_by_product_count.png
│   │
│   └── main_insights.csv
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Datasets

### Customer Dataset

The customer dataset contains demographic and professional variables such as:

- age;
- state;
- salary;
- education level;
- number of children;
- marital status;
- professional area;
- years of professional experience.

It also contains transformed variables created during previous data preparation stages.

### E-commerce Dataset

The e-commerce dataset contains product-related variables such as:

- product title;
- rating;
- number of reviews;
- discount;
- brand;
- material;
- gender category;
- season;
- sales range;
- price.

The original sales information is stored as approximate thresholds such as `+100`, `+1000` and `+10mil`. These labels were converted into numerical minimum estimates for exploratory analysis.

---

## Data Quality and Preparation

Before creating the visualizations, the notebook performs several validation steps:

- confirms that both datasets exist;
- verifies dataset dimensions;
- checks duplicated rows;
- identifies missing values;
- validates selected column names;
- reviews data types;
- converts the customer date column to `datetime`;
- removes an unnecessary CSV index column;
- converts categorical sales ranges into numerical estimates;
- uses logarithmic transformations when necessary for visualization.

Missing values are handled separately for each analysis. Rows are removed only when the variables required for a specific chart are unavailable.

The original datasets are not permanently modified.

---

## Customer Analysis

### Age Distribution

The customer base presents a broad age distribution, with the mean age close to 40 years and the median slightly lower.

### Salary Distribution

Salary is positively skewed. A smaller group of high-income customers increases the overall mean above the median.

Potential outliers were identified statistically but were not automatically removed because they may represent valid customer profiles.

### Professional Experience and Salary

Professional experience presents a moderate positive association with salary. Customers with more years of experience generally tend to have higher incomes, although considerable variation remains.

### Salary by Education Level

Higher education levels are associated with higher mean and median salaries. Postgraduate customers present the highest typical income in the dataset.

### Salary by Professional Area

Technology presents the highest median salary among the analyzed professional areas, followed by Health.

The median was used because it is less affected by extreme salary values.

### Customer Correlations

The strongest customer relationship is between age and professional experience. Professional experience also presents a moderate positive association with salary.

The number of children shows little linear association with the other numerical variables.

---

## E-commerce Analysis

### Product Price Distribution

Product prices are positively skewed. Most products are concentrated in lower and intermediate price ranges, while a smaller group of premium products raises the average.

### Product Distribution by Brand

The catalog contains a large number of different brands, indicating a fragmented product assortment.

Generic labels that did not identify specific brands were excluded from this ranking.

### Estimated Sales by Brand

Some brands lead because they have a broad product catalog, while others achieve high estimated sales with fewer products.

The results represent minimum sales indicators rather than exact transaction totals.

### Reviews and Estimated Sales

The strongest numerical relationship in the e-commerce dataset is between the number of reviews and estimated sales.

The correlation is approximately `0.89`, indicating that products with more reviews generally appear in higher sales categories.

This relationship should not be interpreted as proof of causation. Higher sales may generate more reviews, while products with many reviews may also attract additional customers.

### Discount and Estimated Sales

Discount percentage presents little association with estimated sales.

Higher discounts do not appear to guarantee higher sales in this dataset. However, discount information is available for only part of the product catalog.

### Product Rating and Price

Product ratings show little association with price. Products with similar ratings appear across a wide range of prices.

A higher price therefore does not necessarily correspond to a higher customer rating.

### E-commerce Correlations

Review volume is more closely associated with estimated sales than product price, discount percentage or rating.

---

## Main Insights

- The customer base has a broad demographic profile.
- Salary distribution contains a smaller group of high-income customers.
- Education and professional experience are positively associated with salary.
- Technology has the highest median salary among the professional areas analyzed.
- The e-commerce catalog contains many distinct brands.
- Review volume is a strong indicator of product popularity and estimated commercial activity.
- Discount percentage alone does not explain sales performance.
- Product rating has little relationship with product price.
- Correlation identifies association, not causation.

A structured summary of the main results is available at:

```text
reports/main_insights.csv
```

---

## Project Limitations

The results should be interpreted considering the following limitations:

- the datasets do not share a common customer or transaction identifier;
- customer profiles cannot be connected to specific product purchases;
- the e-commerce dataset contains missing values;
- sales values are approximate thresholds rather than exact quantities;
- the duration of discounts is unknown;
- transaction dates, inventory levels and marketing campaigns are unavailable;
- correlations do not establish causal relationships;
- some product categories contain generic or incomplete labels.

---

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook
- Pathlib

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone <repository-url>
```

### 2. Navigate to the project directory

```bash
cd Data-Science-Portfolio/04-Data-Visualization
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

Linux or macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Open the notebook

```text
notebooks/customer_ecommerce_insights.ipynb
```

Select the project virtual environment as the notebook kernel and run all cells from top to bottom.

---

## Generated Outputs

The notebook automatically generates:

- statistical summaries;
- correlation matrices;
- thirteen visualization files;
- a consolidated insights CSV file.

The charts are saved in:

```text
reports/figures/
```

---

## Conclusion

This project demonstrates how prepared datasets can be transformed into clear demographic and commercial insights through exploratory data analysis and visualization.

It also emphasizes the importance of data validation, appropriate statistical measures, transparent treatment of missing data and careful interpretation of correlations.