import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file.
load_dotenv()

# Accessing the API key from environment variables
api_key = os.getenv('CMC_API_KEY')
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
}


def get_price_change_vs_bitcoin():
    # Endpoint for listings to get Bitcoin ID.
    listings_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    response = requests.get(listings_url, headers=headers)
    data = response.json()['data']
    
    # Find the Bitcoin ID
    bitcoin_id = next(item['id'] for item in data if item['symbol'] == 'BTC')
    
    # Get the current price of Bitcoin
    bitcoin_price = next(item['quote']['USD']['price'] for item in data if item['id'] == bitcoin_id)
    
    # Create a DataFrame to store the data
    df = pd.DataFrame(columns=['Symbol', 'Price (BTC)', 'Change 1h (%)', 'Change 24h (%)'])
    
    # Loop through each cryptocurrency and calculate its price in BTC and its price changes
    for currency in data:
        symbol = currency['symbol']
        price_usd = currency['quote']['USD']['price']
        price_btc = price_usd / bitcoin_price
        change_1h = currency['quote']['USD']['percent_change_1h']
        change_24h = currency['quote']['USD']['percent_change_24h']
        
        # Append to the DataFrame using .loc
        df.loc[len(df)] = [symbol, price_btc, change_1h, change_24h]
    
    return df

# Call the function and print the result
df = get_price_change_vs_bitcoin()
print(df)

# To save the DataFrame as a CSV file
df.to_csv('crypto_price_changes_vs_bitcoin.csv', index=False)
