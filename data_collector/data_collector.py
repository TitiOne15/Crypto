#%% Récupérer l'historique

from dotenv import load_dotenv
import os
import ccxt
import pandas as pd
import time
from datetime import datetime

# Initialiser l'exchange
load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

binance = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True
})

# Définir la paire de trading et le timeframe
symbol = 'ETH/USDT'
timeframe = '1h'

# Récupérer l'historique
ohlcv_data = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=1000)

all_data = []
# Par exemple, démarrer à une date précise (2020-01-01) convertie en timestamp
since = binance.parse8601('2020-01-01T00:00:00Z')

while True:
    ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=1000)
    if not ohlcv:
        break  # si plus de data, on s'arrête
    
    all_data += ohlcv
    # Avancer le 'since' : on prend le dernier timestamp récupéré + 1 ms
    since = ohlcv[-1][0] + 1

    # Optionnel : faire une pause pour respecter les rate limits
    time.sleep(1)

# Convertir en DataFrame  
columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
df = pd.DataFrame(all_data, columns=columns)

# Convertir timestamp en datetime lisible
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
df.set_index('timestamp', inplace=True)
df.sort_index(inplace=True)  # s'assurer que c'est dans l'ordre

#%% Sauvegarder
df.to_parquet('../data/ETH_USDT_1h_raw.parquet')

# %%
