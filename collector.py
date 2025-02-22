# collector.py
import pandas as pd
from binance.client import Client
import os

def collect_data(api_key, api_secret, symbol='ETHUSDT', interval='1h', start_str='1 Jan 2020'):
    client = Client(api_key, api_secret)
    klines = client.get_historical_klines(symbol, interval, start_str)
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

if __name__ == "__main__":
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    data = collect_data(api_key, api_secret)
    data.to_csv('data/eth_usdt.csv')
