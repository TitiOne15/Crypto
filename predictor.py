# predictor.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

def predict_signal(model, data):
    X = data[['open', 'high', 'low', 'close', 'volume', 'rsi', 'macd']]
    signal = model.predict(X)
    return signal

if __name__ == "__main__":
    with open('data/rf_model.pkl', 'rb') as f:
        model = pickle.load(f)
    data = pd.read_csv('data/eth_usdt_preprocessed.csv', index_col='timestamp', parse_dates=True)
    signal = predict_signal(model, data)
    print(signal)
