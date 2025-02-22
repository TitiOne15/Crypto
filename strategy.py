# strategy.py
import pandas as pd

def backtest_strategy(data, signal):
    data['signal'] = signal
    data['strategy_return'] = data['close'].pct_change().shift(-1) * data['signal']
    cumulative_return = (1 + data['strategy_return']).cumprod()
    return cumulative_return

if __name__ == "__main__":
    data = pd.read_csv('data/eth_usdt_preprocessed.csv', index_col='timestamp', parse_dates=True)
    signal = pd.read_csv('data/signal.csv', index_col='timestamp', parse_dates=True)
    cumulative_return = backtest_strategy(data, signal)
    print(cumulative_return)
