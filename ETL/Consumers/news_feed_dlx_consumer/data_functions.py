from common.db_config import pg_db
from common.models.news_data import NewsData
from datetime import datetime
from dateutil import parser
from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer
from bs4 import BeautifulSoup


tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())

def save_news_message(message):
    try:
        # Analyser le sentiment du résumé
        cleaned_summary = clean_summary(message.get('summary', ''))

        sentiment = analyze_sentiment(cleaned_summary)

        # Parser la date de publication
        published_date = parse_published_date(message.get('published'))

        with pg_db.atomic():
            news_data, created = NewsData.get_or_create(
                link=message.get('link'),
                defaults={
                    'title': message.get('title'),
                    'published': published_date,
                    'summary': cleaned_summary,
                    'source': message.get('source'),
                    'image_url': message.get('image_url'),
                    'sentiment': sentiment
                }
            )
            if not created:
                print(f"L'article avec le lien '{message.get('link')}' existe déjà.")
    except Exception as e:
        print(f"Erreur lors de l'insertion des données d'actualités : {e}")
        raise e

def analyze_sentiment(text):
    if not text:
        return 0.0  # 0 si le texte est vide
    try:
        blob = tb(text)
        sentiment = blob.sentiment[0]  # Range entre -1 et 1
        return sentiment
    except Exception as e:
        print(f"Erreur lors de l'analyse de sentiments : {e}")
        return 0.0

def parse_published_date(published_str):
    try:
        return parser.parse(published_str)
    except Exception as e:
        print(f"Erreur lors du parsing de la date : {e}")
        return datetime.now()  # Date de now par défaut
    
def clean_summary(summary):
    soup = BeautifulSoup(summary, 'html.parser')
    return soup.get_text()


