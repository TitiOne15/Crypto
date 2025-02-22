# processor.py
import pandas as pd
import ta

def preprocess_data(file_path):
    data = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
    data['rsi'] = ta.momentum.rsi(data['close'], window=14)
    data['macd'] = ta.trend.macd_diff(data['close'])
    data.dropna(inplace=True)
    return data

if __name__ == "__main__":
    data = preprocess_data('data/eth_usdt.csv')
    data.to_csv('data/eth_usdt_preprocessed.csv')
