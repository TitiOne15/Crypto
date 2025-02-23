# data_collector.py

import requests
import pandas as pd
import os
from datetime import datetime

# CoinGecko API pour récupérer l'historique de prix de l'Ethereum (ETH) en USD
API_URL = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"

# Paramètres pour obtenir l'historique complet ("max") à un intervalle "hourly"
params = {
    "vs_currency": "usd",
    "days": "max",         # 'max' = historique le plus long possible (démarre en 2015-2016)
    "interval": "hourly"   # granularité horaire
}

print("Fetching hourly ETH data from CoinGecko...")
response = requests.get(API_URL, params=params)
if response.status_code != 200:
    raise Exception(f"HTTP Error {response.status_code} - {response.text}")

data = response.json()

# data['prices'] = liste de [ [timestamp_ms, prix], ... ]
prices = data.get("prices", [])          # prix
volumes = data.get("total_volumes", [])  # volumes (en USD)

if not prices:
    raise Exception("No price data returned by CoinGecko.")

# --- Convertir les données en DataFrame pour les prix ---
df_price = pd.DataFrame(prices, columns=["timestamp_ms", "price"])
df_price["timestamp"] = pd.to_datetime(df_price["timestamp_ms"], unit="ms", utc=True)
df_price.set_index("timestamp", inplace=True)
df_price.sort_index(inplace=True)

# --- Convertir les données en DataFrame pour les volumes ---
df_vol = pd.DataFrame(volumes, columns=["timestamp_ms", "volume"])
df_vol["timestamp"] = pd.to_datetime(df_vol["timestamp_ms"], unit="ms", utc=True)
df_vol.set_index("timestamp", inplace=True)
df_vol.sort_index(inplace=True)

# Joindre les deux (sur l’index = timestamp)
df = df_price.join(df_vol[["volume"]], how="outer")

# CoinGecko ne donne qu'un point de prix par heure → On utilise la même valeur pour open/high/low/close
df["open"] = df["price"]
df["high"] = df["price"]
df["low"] = df["price"]
df["close"] = df["price"]

# Réorganiser les colonnes pour un format OHLCV standard
df = df[["open", "high", "low", "close", "volume"]]

# Optionnel : On peut renommer la colonne volume pour clarifier qu'il s'agit d'un "volume en USD"
# df.rename(columns={"volume": "volume_usd"}, inplace=True)

# --- Sauvegarde en Parquet (ou CSV) ---
os.makedirs("data", exist_ok=True)  # Crée le dossier 'data' si inexistant
output_path = "./data/ETH_USDT_1h_raw.parquet"
df.to_parquet(output_path)

print(f"Data collected and saved to {output_path}")
print(df.tail())  # Afficher quelques dernières lignes pour vérifier
