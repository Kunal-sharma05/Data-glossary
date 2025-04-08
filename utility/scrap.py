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
            for cell in table.findAll("td"):
                nested_table = cell.find("table")
                if nested_table:
                    nested_table_df = pd.read_html(str(nested_table))[0]
                    formated_values = "values: " + "|".join(nested_table_df.apply(lambda row: f"{row[0]}-{row[1]}",axis=1))
                    cell.string = formated_values
            # Convert the table to a DataFrame
            df = pd.read_html(StringIO(str(table)))[0]
            df.columns = list(df.columns[:-1]) + ["Possible Values"]
            df.dropna(axis=1, how="all", inplace=True)
            return table_name, df
        else:
            print("No table found in the HTML content.")
            return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

