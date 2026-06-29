# 📚 Project 01 - Web Data Collection

## Overview

This project demonstrates a complete web data collection workflow using Python.

The script extracts book titles and prices from the educational website **Books to Scrape**, converts prices from GBP to BRL using a live exchange rate API, stores the data in a Pandas DataFrame, and exports the final result to a CSV file.

## Data Source

* Website: https://books.toscrape.com/
* Exchange Rate API: Frankfurter API

## Features

* Web scraping with BeautifulSoup
* HTTP requests with Requests
* Live currency conversion from GBP to BRL
* Data organization with Pandas
* CSV export
* Collection date and time registration
* Modular Python code with functions
* English code comments

## Project Structure

```text
01-Data-Collection
│
├── README.md
├── requirements.txt
├── books_catalog.csv
└── src
    └── books_scraping.py
```

## Output Columns

The generated CSV file contains:

* Collection DateTime
* Title
* Price (GBP)
* Exchange Rate (GBP to BRL)
* Price (BRL)

## How to Run

From the root folder of the repository, run:

```bash
python 01-Data-Collection/src/books_scraping.py
```

## Technologies Used

* Python
* Requests
* BeautifulSoup4
* Pandas
* Frankfurter API

## Future Improvements

* Extract book ratings
* Extract stock availability
* Scrape all pages from the website
* Save the data in SQLite
* Create a dashboard with the collected data

## Author

**Luan Putinati Lorencetti**

Data Science Portfolio
