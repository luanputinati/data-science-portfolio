# Import required libraries
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_exchange_rate(base_currency, target_currency):
    # Define the exchange rate API URL
    url = "https://api.frankfurter.dev/v1/latest"

    # Define the request parameters
    params = {"base": base_currency, "symbols": target_currency}

    # Send a GET request to the exchange rate API
    response = requests.get(url, params=params, timeout=10)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch exchange rate. Status code: {response.status_code}"
        )

    # Convert the API response to JSON
    data = response.json()

    # Extract and return the exchange rate
    return data["rates"][target_currency]


def collect_books(url, exchange_rate, collection_datetime):
    # Send an HTTP GET request to the website
    response = requests.get(url, timeout=10)

    # Set the correct encoding
    response.encoding = "utf-8"

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(
            f"Failed to access website. Status code: {response.status_code}"
        )

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Create an empty list to store book data
    catalog = []

    # Find all book articles on the page
    for article in soup.find_all("article", class_="product_pod"):

        # Extract the book title
        title = article.find("h3").a["title"]

        # Extract the book price in GBP as text
        price_gbp_text = article.find("p", class_="price_color").text

        # Remove the currency symbol and convert the price to float
        price_gbp = float(price_gbp_text.replace("£", ""))

        # Convert the GBP price to BRL
        price_brl = round(price_gbp * exchange_rate, 2)

        # Store the extracted data in a dictionary
        book = {
            "Collection DateTime": collection_datetime,
            "Title": title,
            "Price (GBP)": price_gbp,
            "Exchange Rate (GBP to BRL)": round(exchange_rate, 4),
            "Price (BRL)": price_brl,
        }

        # Add the book dictionary to the catalog list
        catalog.append(book)

    # Return the final catalog
    return catalog


def export_to_csv(catalog, file_path):
    # Convert the catalog list into a Pandas DataFrame
    dataframe = pd.DataFrame(catalog)

    # Export the DataFrame to a CSV file
    dataframe.to_csv(file_path, index=False, encoding="utf-8-sig")

    # Return the DataFrame
    return dataframe


def display_summary(url, exchange_rate, total_books, file_path, collection_datetime):
    # Display a professional execution summary
    print("=" * 60)
    print("BOOKS TO SCRAPE - DATA COLLECTION PROJECT")
    print("=" * 60)
    print(f"Website: {url}")
    print(f"Collection date and time: {collection_datetime}")
    print(f"Exchange rate used: 1 GBP = R$ {exchange_rate:.4f}")
    print(f"Books collected: {total_books}")
    print(f"CSV exported to: {file_path}")
    print("=" * 60)


def main():
    # Define the target website
    books_url = "https://books.toscrape.com/"

    # Define the output CSV file path
    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = BASE_DIR / "books_catalog.csv"

    # Register the collection date and time
    collection_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch the live exchange rate from GBP to BRL
    exchange_rate = get_exchange_rate("GBP", "BRL")

    # Collect book data from the website
    catalog = collect_books(books_url, exchange_rate, collection_datetime)

    # Export collected data to CSV
    dataframe = export_to_csv(catalog, file_path)

    # Display the collected data
    print(dataframe)

    # Display execution summary
    display_summary(
        books_url, exchange_rate, len(catalog), file_path, collection_datetime
    )


# Run the main function only when this file is executed directly
if __name__ == "__main__":
    main()
