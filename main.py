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
    # Endpoint for listings to get Bitcoin ID and price changes.
    listings_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    response = requests.get(listings_url, headers=headers)
    data = response.json()['data']
    
    # Find the Bitcoin data
    bitcoin_data = next(item for item in data if item['symbol'] == 'BTC')
    
    # Get the current price of Bitcoin and its percentage changes
    bitcoin_price = bitcoin_data['quote']['USD']['price']
    bitcoin_change_1h = bitcoin_data['quote']['USD']['percent_change_1h']
    bitcoin_change_24h = bitcoin_data['quote']['USD']['percent_change_24h']
    
    # Create a DataFrame to store the data
    df = pd.DataFrame(columns=['Symbol', 'Price (SATS)', 'Relative Change 1h (%)', 'Relative Change 24h (%)'])
    
    # Loop through each cryptocurrency and calculate its price in Satoshis and relative price changes
    for currency in data:
        symbol = currency['symbol']
        price_usd = currency['quote']['USD']['price']
        price_sats = round(price_usd / bitcoin_price * 100000000, 1)
        
        # Calculate relative changes
        change_1h = currency['quote']['USD']['percent_change_1h']
        relative_change_1h = round(change_1h - bitcoin_change_1h, 1)
        
        change_24h = currency['quote']['USD']['percent_change_24h']
        relative_change_24h = round(change_24h - bitcoin_change_24h, 1)
        
        # Append to the DataFrame using .loc
        df.loc[len(df)] = [symbol, price_sats, relative_change_1h, relative_change_24h]
    
    return df

# Call the function and print the result
df = get_price_change_vs_bitcoin()
print(df)

# To save the DataFrame as a CSV file
df.to_csv('crypto_relative_price_changes_vs_bitcoin.csv', index=False)
