import os
import requests
import tweepy
import telegram_send
from bs4 import BeautifulSoup
from datetime import datetime

class SimpleNewsAnalyzer:
    def __init__(self):
        self.news_items = []
        
    def get_crypto_news(self):
        # Récupère les news de CoinGecko (API gratuite)
        try:
            response = requests.get('https://api.coingecko.com/api/v3/news')
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erreur lors de la récupération des news: {e}")
        return []

    def get_twitter_mentions(self):
        # Configuration basique de Twitter
        auth = tweepy.OAuthHandler(os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET'))
        api = tweepy.API(auth)
        
        # Recherche des tweets pertinents
        search_terms = ["#bitcoin", "#btc", "crypto"]
        tweets = []
        for term in search_terms:
            try:
                tweets.extend(api.search_tweets(q=term, lang="en", count=10))
            except Exception as e:
                print(f"Erreur Twitter: {e}")
        return tweets

    def analyze_importance(self, item):
        # Analyse simple basée sur des mots-clés
        important_keywords = ['regulation', 'SEC', 'ETF', 'hack', 'adoption']
        score = 0
        for keyword in important_keywords:
            if keyword.lower() in str(item).lower():
                score += 2
        return min(score, 10)  # Score maximum de 10

    def analyze_risk(self, item):
        # Analyse simple des risques
        risk_keywords = ['hack', 'ban', 'crash', 'risk', 'warning']
        score = 0
        for keyword in risk_keywords:
            if keyword.lower() in str(item).lower():
                score += 2
        return min(score, 10)

    def run_analysis(self):
        # Récupération des news
        news = self.get_crypto_news()
        
        # Analyse et formatage
        analyzed_items = []
        for item in news:
            analyzed_item = {
                'title': item.get('title', ''),
                'source': item.get('url', ''),
                'importance': self.analyze_importance(item),
                'risk': self.analyze_risk(item),
                'timestamp': datetime.now().isoformat()
            }
            analyzed_items.append(analyzed_item)

        # Filtrage des items importants (score > 5)
        important_items = [item for item in analyzed_items if item['importance'] > 5 or item['risk'] > 5]
        
        # Envoi des résultats via Telegram
        self.send_telegram_report(important_items)
        
        return important_items

    def send_telegram_report(self, items):
        if not items:
            return
            
        message = "🔔 Rapport Bitcoin quotidien:\n\n"
        for item in items:
            message += f"📌 {item['title']}\n"
            message += f"Importance: {'🟥' * (item['importance']//2)}\n"
            message += f"Risque: {'⚠️' * (item['risk']//2)}\n"
            message += f"Source: {item['source']}\n\n"
            
        try:
            telegram_send.send(messages=[message])
        except Exception as e:
            print(f"Erreur Telegram: {e}")

if __name__ == "__main__":
    analyzer = SimpleNewsAnalyzer()
    analyzer.run_analysis()
