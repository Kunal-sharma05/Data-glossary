from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO


def scrape_table_from_url(url):
    try:

        table_name = url.split("/")[-1].split('.')[0]

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table")

        if table:
            # Convert the table to a DataFrame
            df = pd.read_html(StringIO(str(table)))[0]
            return table_name, df
        else:
            print("No table found in the HTML content.")
            return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

