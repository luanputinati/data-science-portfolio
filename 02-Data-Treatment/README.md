# Customer Data Quality Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-purple)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

A reproducible data-quality pipeline developed with Python and Pandas
to diagnose, clean, validate, audit and anonymize customer registration
data.

The project was created during the Data Treatment module of my Data
Science training and expanded from a classroom exercise into a
portfolio-ready application.

## Project overview

The original dataset contains customer registration information with
quality problems such as:

- missing values;
- duplicated records;
- invalid ages;
- inconsistent geographic information;
- incomplete registrations;
- sensitive personal data;
- columns requiring type and text normalization.

The pipeline processes the dataset through five automated stages:

```text
Raw data
   ↓
Initial profiling
   ↓
Cleaning and standardization
   ↓
Validation and auditing
   ↓
Anonymization
   ↓
Quality report and charts
```

## Main results

| Metric | Result |
|---|---:|
| Initial records | 1,027 |
| Records after deduplication | 1,018 |
| Removed duplicates | 9 |
| Missing values in the original dataset | 30 |
| Rows containing missing values | 29 |
| Missing or invalid CPFs | 7 |
| Invalid ages | 16 |
| Ages inconsistent with birth date | 0 |
| State and address UF inconsistencies | 968 |
| Incomplete registrations | 19 |
| Records with at least one inconsistency | 971 |
| Records without identified inconsistencies | 47 |
| Consistency rate | 4.62% |

The high number of geographic inconsistencies was preserved for
auditing. The pipeline does not automatically choose whether the state
column or the address UF is correct.

## Quality issues

![Quality issues](reports/figures/problemas_qualidade.png)

## Age distribution

![Age distribution](reports/figures/distribuicao_faixas_etarias.png)

## Project structure

```text
02-Data-Treatment/
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   └── sample/
│       └── clientes_demo.csv
├── reports/
│   ├── figures/
│   │   ├── distribuicao_faixas_etarias.png
│   │   └── problemas_qualidade.png
│   ├── diagnostico_inicial.md
│   └── relatorio_qualidade.md
├── src/
│   ├── anonymization.py
│   ├── cleaning.py
│   ├── diagnostico_inicial.py
│   ├── main.py
│   ├── reporting.py
│   └── validation.py
└── README.md
```

## Pipeline stages

### 1. Initial profiling

The profiling stage inspects:

- dataset dimensions;
- column types;
- missing values;
- duplicated rows;
- descriptive statistics;
- age distribution.

Generated file:

```text
reports/diagnostico_inicial.md
```

### 2. Cleaning and standardization

The cleaning stage:

- removes complete duplicates;
- standardizes customer names;
- preserves CPF values as strings;
- removes CPF punctuation;
- converts birth dates;
- normalizes addresses, states and countries;
- identifies ages outside the valid range;
- flags incomplete registrations.

### 3. Validation and auditing

The validation stage:

- validates CPF check digits;
- recalculates ages from birth dates;
- compares reported and calculated ages;
- extracts the UF from addresses;
- converts Brazilian state names to UF codes;
- identifies geographic inconsistencies;
- records the reason for each inconsistency.

The reference date adopted for age validation is April 4, 2024, based
on the temporal context inferred from the dataset.

### 4. Anonymization

The public sample removes direct identifiers such as:

- names;
- CPFs;
- full addresses;
- exact birth dates;
- exact ages.

Exact ages are replaced with age ranges, and synthetic identifiers such
as `CLI-0001` are generated.

[View the anonymized sample](data/sample/clientes_demo.csv)

### 5. Reporting

The reporting stage produces aggregated quality indicators and charts
without publishing personal data.

[View the complete quality report](reports/relatorio_qualidade.md)

## Running the project

From the repository root, activate the virtual environment:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Place the original dataset at:

```text
02-Data-Treatment/data/raw/clientes.csv
```

Run the complete pipeline:

```bash
python 02-Data-Treatment/src/main.py
```

Individual stages can also be executed separately:

```bash
python 02-Data-Treatment/src/diagnostico_inicial.py
python 02-Data-Treatment/src/cleaning.py
python 02-Data-Treatment/src/validation.py
python 02-Data-Treatment/src/anonymization.py
python 02-Data-Treatment/src/reporting.py
```

## Privacy

The raw and processed datasets contain sensitive-looking customer
registration data and are excluded from version control through
`.gitignore`.

Only aggregated reports, charts and an anonymized sample are publicly
available.

## Technologies

- Python
- Pandas
- Matplotlib
- pathlib
- regular expressions
- Markdown
- Git and GitHub

## Skills demonstrated

- data profiling;
- missing-value analysis;
- duplicate removal;
- text normalization;
- type conversion;
- rule-based validation;
- CPF validation;
- outlier treatment;
- geographic consistency checks;
- privacy-aware data anonymization;
- automated reporting;
- reproducible pipeline design.