import logging
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_news.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Dans la classe CryptoNewsAnalyzer, modifiez la méthode run_analysis :
def run_analysis(self):
    logging.info("Démarrage de l'analyse")
    try:
        news = self.get_crypto_news()
        logging.info(f"Récupération de {len(news)} articles")
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des news: {e}")
        news = []

    try:
        tweets = self.get_twitter_mentions()
        logging.info(f"Récupération de {len(tweets)} tweets")
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des tweets: {e}")
        tweets = []

    analyzed_items = []
    
    for item in news + tweets:
        try:
            title = item.get('title', item.get('text', ''))
            logging.debug(f"Analyse de: {title[:50]}...")
            
            if self.is_duplicate(title):
                logging.debug("Article dupliqué, ignoré")
                continue
                
            analyzed_item = {
                'title': title,
                'source': item.get('url', item.get('source', {}).get('url', '')),
                'importance': self.analyze_importance(item),
                'risk': self.analyze_risk(item),
                'timestamp': datetime.now().isoformat()
            }
            
            logging.debug(f"Scores - Importance: {analyzed_item['importance']}, Risque: {analyzed_item['risk']}")
            
            self.cache[self.get_hash(title)] = analyzed_item
            
            if analyzed_item['importance'] > 3 or analyzed_item['risk'] > 3:
                analyzed_items.append(analyzed_item)
                
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse d'un item: {e}")
    
    self.save_cache()
    
    if analyzed_items:
        logging.info(f"Envoi de {len(analyzed_items)} alertes")
        message = self.format_telegram_message(analyzed_items)
        try:
            telegram_send.send(messages=[message])
            logging.info("Message Telegram envoyé avec succès")
        except Exception as e:
            logging.error(f"Erreur Telegram: {e}")
            logging.error(f"Message qui a échoué: {message[:200]}...")
    else:
        logging.info("Aucune alerte à envoyer")
    
    return analyzed_items
