import os
from dotenv import load_dotenv
import pandas as pd
import requests
from langchain.tools import tool
import time
load_dotenv()

@tool
def stock_prices_tool(stock_name):

    """Function to fetch stock prices from Alpha Vantage"""

    alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
 

    try:
        url = "https://" + f"www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name.replace(' ','%20')}&apikey={alpha_vantage_api_key}"
        r = requests.get(url)
        data = r.json()
    except Exception as e:
        print(f"Alpha Vantage API Error occurred: \n {e}")
        
    try:
        stock_ticker = ''
        for match in data['bestMatches']:
            if 'BSE' in match['1. symbol']:
               stock_ticker = match['1. symbol']
        
        if stock_ticker == '':
            raise ValueError('Stock not found in BSE')
    except Exception as e:
        raise TypeError(data)

    time.sleep(5)

    try:
        try:
            url = "https://" + f"www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_ticker}&apikey={alpha_vantage_api_key}"
            r = requests.get(url)
            data = r.json()
        except Exception as e:
            print(f"Alpha Vantage API Error occurred: \n {e}")

        stock_prices_json = data['Time Series (Daily)']
    except Exception as e:
        raise TypeError(data)

    time.sleep(5)

    stock_prices_df = pd.DataFrame(stock_prices_json).T
    stock_prices_df.rename(columns={'1. open':'open','2. high':'high','3. low':'low','4. close':'close','5. volume':'volume'},inplace=True)
    stock_prices_df.reset_index(inplace=True)
    stock_prices_df.rename(columns={'index':'date'},inplace=True)

    stock_prices_mkd = stock_prices_df.to_markdown(index=False)

    return stock_prices_mkd