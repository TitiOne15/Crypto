import requests
import pandas as pd
import time
from datetime import datetime, timedelta

def get_hourly_data_coingecko(
    start_date: str = "2016-01-01", 
    end_date: str   = "2025-01-01"
):
    """
    Récupère de l'historique horaire ETH depuis start_date jusqu'à end_date,
    en découpant la période en segments de 90 jours pour respecter les limites de l'API.
    start_date et end_date au format 'YYYY-MM-DD'.
    """
    # Convertir en timestamps UNIX (secondes)
    start_ts = int(pd.to_datetime(start_date).timestamp())
    end_ts   = int(pd.to_datetime(end_date).timestamp())

    # Nombre de jours entre start_date et end_date
    total_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days

    # Avance par segments de 90 jours max
    chunk_size = 90
    df_list = []

    current_start = start_ts
    while True:
        # Déterminer la date de fin du chunk (90 jours plus tard ou end_date si on dépasse)
        chunk_end = current_start + (chunk_size * 24 * 3600)
        if chunk_end > end_ts:
            chunk_end = end_ts

        print(f"Fetching chunk from {current_start} to {chunk_end}...")

        # Appel API
        url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart/range"
        params = {
            "vs_currency": "usd",
            "from": current_start,
            "to": chunk_end
        }

        r = requests.get(url, params=params)
        if r.status_code != 200:
            raise Exception(f"Error {r.status_code} - {r.text}")

        data = r.json()

        # Extraire 'prices' et 'total_volumes'
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])

        # Conversion en DataFrame
        df_price = pd.DataFrame(prices, columns=["timestamp_ms", "price"])
        df_price["timestamp"] = pd.to_datetime(df_price["timestamp_ms"], unit="ms", utc=True)
        df_price.set_index("timestamp", inplace=True)

        df_vol   = pd.DataFrame(volumes, columns=["timestamp_ms", "volume"])
        df_vol["timestamp"] = pd.to_datetime(df_vol["timestamp_ms"], unit="ms", utc=True)
        df_vol.set_index("timestamp", inplace=True)

        df_merged = df_price.join(df_vol[["volume"]], how="outer")
        df_merged.sort_index(inplace=True)

        df_list.append(df_merged)

        # Arrêter si on a atteint la fin
        if chunk_end >= end_ts:
            break

        # Passer au chunk suivant
        current_start = chunk_end
        time.sleep(1)  # Respecter un peu de délai pour éviter le rate limit

    # Concaténer toutes les tranches
    df_final = pd.concat(df_list)
    df_final = df_final[~df_final.index.duplicated(keep='first')]  # enlever doublons éventuels

    # Reconstruire OHLCV en assumant la même valeur pour open/high/low/close
    df_final["open"]  = df_final["price"]
    df_final["high"]  = df_final["price"]
    df_final["low"]   = df_final["price"]
    df_final["close"] = df_final["price"]

    df_final = df_final[["open", "high", "low", "close", "volume"]]
    df_final.sort_index(inplace=True)
    return df_final


if __name__ == "__main__":

    # Exemple : de 2016-01-01 à 2021-01-01 en hourly
    df = get_hourly_data_coingecko("2016-01-01", "2021-01-01")

    print(df.head(), df.tail(), df.shape)

    # Sauvegarde
    df.to_csv("ETH_hourly_2016_2021.csv")
