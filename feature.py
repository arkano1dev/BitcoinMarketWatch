import csv
import requests
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv('CMC_API_KEY')
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
}

def get_current_prices(currencies):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {'symbol': ','.join(currencies)}
    response = requests.get(url, headers=headers, params=parameters)
    data = response.json().get('data', {})
    
    btc_price_usd = Decimal(data['BTC']['quote']['USD']['price']).quantize(Decimal('0.01'), rounding=ROUND_DOWN) if 'BTC' in data else None
    prices = {
        currency: {
            'price_usd': Decimal(data[currency]['quote']['USD']['price']).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
            'price_btc': (Decimal(data[currency]['quote']['USD']['price']) / btc_price_usd).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        } for currency in currencies if currency in data
    }
    
    return prices, btc_price_usd

def read_portfolio(path):
    portfolio = []
    with open(path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            portfolio.append({
                'currency': row['currency'],
                'amount': Decimal(row['amount']),
                'average_purchase_price': Decimal(row['average_purchase_price']).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            })
    return portfolio

def calculate_portfolio_value(portfolio, prices, btc_price_usd):
    total_initial_value_usd = sum(Decimal(asset['amount']) * Decimal(asset['average_purchase_price']) for asset in portfolio)
    total_current_value_usd = Decimal('0')
    total_current_value_btc = Decimal('0')

    # Enhanced portfolio calculations
    for asset in portfolio:
        currency = asset['currency']
        if currency in prices:
            current_price_usd = prices[currency]['price_usd']
            current_price_btc = prices[currency]['price_btc']
            asset['current_price_usd'] = current_price_usd.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            asset['current_price_btc'] = current_price_btc.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
            asset['value_usd'] = (Decimal(asset['amount']) * current_price_usd).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            asset['value_btc'] = (Decimal(asset['amount']) * current_price_btc).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
            asset['pl_usd'] = (asset['value_usd'] - (Decimal(asset['amount']) * Decimal(asset['average_purchase_price']))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            asset['pl_percent_usd'] = ((asset['value_usd'] / (Decimal(asset['amount']) * Decimal(asset['average_purchase_price'])) - 1) * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if asset['average_purchase_price'] != Decimal('0') else Decimal('0')
            asset['pl_btc'] = (asset['value_btc'] - (Decimal(asset['amount']) * Decimal(asset['average_purchase_price']) / btc_price_usd)).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
            asset['pl_percent_btc'] = ((asset['value_btc'] / (Decimal(asset['amount']) * Decimal(asset['average_purchase_price']) / btc_price_usd) - 1) * 100).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP) if asset['average_purchase_price'] != Decimal('0') else Decimal('0')
            total_current_value_usd += asset['value_usd']
            total_current_value_btc += asset['value_btc']

    return portfolio, total_current_value_usd, total_current_value_btc


def save_to_csv(portfolio, total_value_usd, total_value_btc, filename="portfolio_history.csv"):
    fieldnames = ['currency', 'amount', 'average_purchase_price', 'current_price_usd', 'current_price_btc', 'value_usd', 'value_btc', 'pl_usd', 'pl_percent_usd', 'pl_btc', 'pl_percent_btc', 'date']
    with open(filename, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if the file is new
        if os.stat(filename).st_size == 0:
            writer.writeheader()
        
        for asset in portfolio:
            asset['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow({
                'currency': asset['currency'],
                'amount': asset['amount'],
                'average_purchase_price': asset['average_purchase_price'],
                'current_price_usd': asset['current_price_usd'],
                'current_price_btc': asset['current_price_btc'],
                'value_usd': asset['value_usd'],
                'value_btc': asset['value_btc'],
                'pl_usd': asset['pl_usd'],
                'pl_percent_usd': asset['pl_percent_usd'],
                'pl_btc': asset['pl_btc'],
                'pl_percent_btc': asset['pl_percent_btc'],
                'date': asset['date']
            })

        # Add a total row
        writer.writerow({
            'currency': 'Total',
            'amount': '',
            'average_purchase_price': '',
            'current_price_usd': '',
            'current_price_btc': '',
            'value_usd': total_value_usd,
            'value_btc': total_value_btc,
            'pl_usd' : "" ,
            'pl_percent_usd': "",
            'pl_btc':"",
            'pl_percent_btc': "",
            'date': ""
        })

def main():
    portfolio_path = 'portfolio.csv'
    currencies = ['BTC']  # Initialize with BTC since we'll need its price for conversions
    portfolio = read_portfolio(portfolio_path)
    currencies.extend([asset['currency'] for asset in portfolio if asset['currency'] != 'BTC'])
    
    prices, btc_price_usd = get_current_prices(currencies)
    portfolio, total_value_usd, total_value_btc = calculate_portfolio_value(portfolio, prices, btc_price_usd)
    save_to_csv(portfolio, total_value_usd, total_value_btc)

if __name__ == "__main__":
    main()
