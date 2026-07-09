# Customer Feature Engineering & Preprocessing Pipeline

A customer data preparation pipeline developed as the third mini-project in a Data Science portfolio.

The project transforms a raw dataset into a de-identified, validated, and structured dataset ready for analysis, visualization, and future Machine Learning applications.

## Project Objective

Build a reproducible data preparation pipeline capable of:

- diagnosing data quality issues;
- identifying missing, duplicated, and unique values;
- validating data consistency rules;
- removing personally identifiable information;
- handling missing values;
- creating new features;
- standardizing and normalizing numerical variables;
- encoding categorical variables;
- exporting a prepared dataset;
- automatically generating a Markdown report.

## Results

| Metric | Result |
|---|---:|
| Initial records | 10,000 |
| Initial columns | 13 |
| Fully duplicated rows | 0 |
| Distinct duplicated CPFs | 14 |
| Records removed due to conflicting CPFs | 28 |
| Final records | 9,972 |
| Final columns | 63 |
| Missing values in the final dataset | 0 |
| Features created | 5 |
| One-Hot encoded columns | 39 |

## Pipeline Stages

### 1. Initial Data Diagnosis

The dataset is analyzed to identify:

- dataset dimensions;
- data types;
- missing values;
- percentage of missing values;
- unique values;
- duplicated rows;
- duplicated CPFs;
- descriptive statistics for numerical variables.

### 2. Data Consistency Validation

The pipeline checks for:

- invalid dates;
- ages outside the 18-to-100 range;
- non-positive salaries;
- number of children outside the expected range;
- negative professional experience;
- professional experience greater than age;
- estimated career starting age below 14;
- CPFs associated with conflicting identities;
- constant columns.

### 3. Data De-identification

To reduce the risk of exposing personal information:

- records associated with conflicting CPFs are removed;
- an artificial identifier named `cliente_id` is created;
- the birth year is extracted from the original date;
- the `nome`, `cpf`, `data`, `endereco`, and `pais` columns are removed.

The `pais` column is also removed because it contains only one unique value.

### 4. Missing Value Treatment

The following strategies are applied:

- `salario`: filled with the median;
- categorical variables: filled with `Não informado`;
- creation of `salario_ausente`, indicating whether the salary was originally missing.

The calculated median salary was approximately **BRL 6,061.63**.

### 5. Feature Engineering

Five new variables were created:

| Feature | Description |
|---|---|
| `faixa_etaria` | Groups customers by age range |
| `faixa_experiencia` | Groups customers by years of professional experience |
| `salario_anual` | Monthly salary multiplied by 12 |
| `tem_filhos` | Binary indicator showing whether the customer has children |
| `idade_inicio_carreira` | Estimated career starting age |

### 6. Standardization and Normalization

`StandardScaler` is applied to:

- `salario`;
- `anos_experiencia`.

`MinMaxScaler` is applied to:

- `idade`;
- `numero_filhos`;
- `idade_inicio_carreira`.

The normalized variables are transformed to a range between `0` and `1`.

### 7. Categorical Variable Encoding

`OrdinalEncoder` is used for categories with a natural order:

- `nivel_educacao`;
- `faixa_etaria`;
- `faixa_experiencia`.

`OneHotEncoder` is used for nominal categories:

- `estado`;
- `estado_civil`;
- `area_atuacao`.

This process generated 39 binary columns.

### 8. Data Export and Report Generation

At the end of the execution, the pipeline generates:

```text
data/processed/clientes_preparados.csv
reports/relatorio_preparacao.md
```

The Markdown report contains the main results from every pipeline stage.

## Project Structure

```text
03-Data-Preparing/
├── data/
│   ├── raw/
│   │   └── clientes-v2.csv
│   └── processed/
│       └── clientes_preparados.csv
├── reports/
│   └── relatorio_preparacao.md
├── src/
│   ├── __init__.py
│   └── data_preparation.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

The CSV files located in the `raw` and `processed` directories are not committed to GitHub.

## Technologies

- Python
- pandas
- scikit-learn
- pathlib

Main scikit-learn components:

- `StandardScaler`;
- `MinMaxScaler`;
- `OrdinalEncoder`;
- `OneHotEncoder`.

## Installation

Clone the repository and access its directory:

```bash
git clone <REPOSITORY_URL>
cd data-science-portfolio
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Linux:

```bash
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install -r 03-Data-Preparing/requirements.txt
```

## Dataset Setup

Place the original dataset at:

```text
03-Data-Preparing/data/raw/clientes-v2.csv
```

The filename must remain unchanged so the pipeline can locate it automatically.

## Running the Pipeline

From the repository root directory:

```bash
python 03-Data-Preparing/main.py
```

The pipeline can also be executed from inside the project directory:

```bash
cd 03-Data-Preparing
python main.py
```

After every stage has been completed successfully, the terminal displays:

```text
PIPELINE CONCLUÍDO COM SUCESSO
```

## Automated Validations

During execution, the pipeline stops when it detects issues such as:

- personally identifiable columns remaining in the de-identified dataset;
- missing or duplicated `cliente_id` values;
- missing values remaining after treatment;
- expected features not being created;
- normalized values outside the 0-to-1 range;
- negative ordinal codes;
- unexpected changes in the number of records;
- failure to create the prepared CSV file or Markdown report.

## Data Privacy

The raw dataset contains identifying fields and must not be published.

The `.gitignore` file prevents raw and processed CSV files from being tracked by Git. Only the source code and consolidated report are intended for the public repository.

The de-identification strategy used in this project is intended for educational purposes. In production environments, anonymization methods must consider the data processing context, its purpose, applicable privacy requirements, and re-identification risks.

## Key Learnings

This project demonstrates knowledge of:

- data quality diagnosis;
- missing value treatment;
- consistency validation;
- data de-identification;
- feature engineering;
- standardization and normalization;
- ordinal encoding;
- One-Hot Encoding;
- reproducible data pipelines;
- automated report generation.

## Next Steps

The prepared dataset can be reused in the next portfolio module for:

- exploratory data analysis;
- chart creation;
- pattern identification;
- data visualization;
- dashboard development.