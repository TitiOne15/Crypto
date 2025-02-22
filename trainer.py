# trainer.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle

def train_model(file_path):
    data = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
    X = data[['open', 'high', 'low', 'close', 'volume', 'rsi', 'macd']]
    y = (data['close'].shift(-1) > data['close']).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print('Accuracy:', accuracy_score(y_test, y_pred))
    print('Precision:', precision_score(y_test, y_pred))
    print('Recall:', recall_score(y_test, y_pred))
    print('F1 Score:', f1_score(y_test, y_pred))
    with open('data/rf_model.pkl', 'wb') as f:
        pickle.dump(model, f)

if __name__ == "__main__":
    train_model('data/eth_usdt_preprocessed.csv')
