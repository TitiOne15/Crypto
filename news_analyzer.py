import os
import requests
import tweepy
import telegram_send
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
import json

class CryptoNewsAnalyzer:
    def __init__(self):
        self.news_items = []
        self.cache_file = 'news_cache.json'
        self.load_cache()
        
    def load_cache(self):
        try:
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
                # Nettoyage des entrées plus vieilles que 24h
                self.cache = {k:v for k,v in self.cache.items() 
                            if datetime.fromisoformat(v['timestamp']) > datetime.now() - timedelta(days=1)}
        except:
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def get_hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()

    def is_duplicate(self, text):
        hash_id = self.get_hash(text)
        return hash_id in self.cache

    def get_crypto_news(self):
        sources = [
            'https://api.coingecko.com/api/v3/news',
            'https://api.coinpaprika.com/v1/news',
            'https://cryptopanic.com/api/v1/posts/?auth_token=' + os.getenv('CRYPTOPANIC_TOKEN', '')
        ]
        
        news = []
        for source in sources:
            try:
                response = requests.get(source)
                if response.status_code == 200:
                    news.extend(response.json())
            except Exception as e:
                print(f"Erreur source {source}: {e}")
        return news

    def get_twitter_mentions(self):
        accounts = [
            'whale_alert',
            'BitcoinMagazine',
            'DocumentingBTC',
            'cz_binance'
        ]
        
        auth = tweepy.OAuthHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET')
        )
        api = tweepy.API(auth)
        
        tweets = []
        for account in accounts:
            try:
                user_tweets = api.user_timeline(screen_name=account, count=5)
                tweets.extend(user_tweets)
            except Exception as e:
                print(f"Erreur Twitter {account}: {e}")
        return tweets

    def analyze_importance(self, item):
        important_keywords = {
            'regulation': 3,
            'SEC': 3,
            'ETF': 3,
            'hack': 4,
            'adoption': 2,
            'institutional': 2,
            'halving': 3,
            'fork': 2,
            'upgrade': 2,
            'CBDC': 2
        }
        
        text = str(item).lower()
        score = 0
        for keyword, weight in important_keywords.items():
            if keyword in text:
                score += weight
        return min(score, 10)

    def analyze_risk(self, item):
        risk_keywords = {
            'hack': 5,
            'security breach': 5,
            'ban': 4,
            'crash': 3,
            'bearish': 2,
            'sell-off': 2,
            'regulation': 3,
            'investigation': 3,
            'lawsuit': 4,
            'exploit': 4
        }
        
        text = str(item).lower()
        score = 0
        for keyword, weight in risk_keywords.items():
            if keyword in text:
                score += weight
        return min(score, 10)

    def format_telegram_message(self, items):
        message = "🔔 Mise à jour Bitcoin & Crypto\n\n"
        
        # Tri par importance + risque
        items.sort(key=lambda x: x['importance'] + x['risk'], reverse=True)
        
        for item in items[:5]:  # Top 5 news les plus importantes
            importance_emoji = '🔴' if item['importance'] > 7 else '🟡' if item['importance'] > 4 else '🟢'
            risk_emoji = '⚠️' if item['risk'] > 7 else '⚡' if item['risk'] > 4 else '✔️'
            
            message += f"{importance_emoji} {item['title']}\n"
            message += f"Importance: {item['importance']}/10 {risk_emoji} Risque: {item['risk']}/10\n"
            if 'price_impact' in item:
                message += f"Impact prix: {item['price_impact']}\n"
            message += f"Source: {item['source']}\n\n"
            
        return message

    def run_analysis(self):
        news = self.get_crypto_news()
        tweets = self.get_twitter_mentions()
        
        analyzed_items = []
        
        # Traitement des nouvelles sources
        for item in news + tweets:
            title = item.get('title', item.get('text', ''))
            if self.is_duplicate(title):
                continue
                
            analyzed_item = {
                'title': title,
                'source': item.get('url', item.get('source', {}).get('url', '')),
                'importance': self.analyze_importance(item),
                'risk': self.analyze_risk(item),
                'timestamp': datetime.now().isoformat()
            }
            
            # Sauvegarde dans le cache
            self.cache[self.get_hash(title)] = analyzed_item
            
            if analyzed_item['importance'] > 3 or analyzed_item['risk'] > 3:
                analyzed_items.append(analyzed_item)
        
        self.save_cache()
        
        if analyzed_items:
            message = self.format_telegram_message(analyzed_items)
            try:
                telegram_send.send(messages=[message])
            except Exception as e:
                print(f"Erreur Telegram: {e}")
        
        return analyzed_items

if __name__ == "__main__":
    analyzer = CryptoNewsAnalyzer()
    analyzer.run_analysis()
