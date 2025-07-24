import os
import pika
import feedparser # pip install feedparser
import json
import time
import traceback
from datetime import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Configuration de MongoDB
MONGODB_HOST = os.environ.get('MONGODB_HOST', 'mongodb')
MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
MONGO_ROOT_USER = os.environ.get('MONGO_ROOT_USER', 'root')
MONGO_ROOT_PASSWORD = os.environ.get('MONGO_ROOT_PASS', 'root')

# Configuration de RabbitMQ
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', '/')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'admin')

QUEUE_NAME = "news_feed_queue"

# Connexion à MongoDB
client = MongoClient(
    host=MONGODB_HOST, 
    port=MONGODB_PORT,
    username=MONGO_ROOT_USER,
    password=MONGO_ROOT_PASSWORD,
)
db = client["crypto_db"]
collection = db["news_feed"]

def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials)
    max_retries = 10
    retry_delay = 5  # toujours en secondes :D

    for attempt in range(1, max_retries + 1):
        try:
            connection = pika.BlockingConnection(parameters)
            print("Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection attempt {attempt} failed: {e}")
            if attempt == max_retries:
                print("Max retries atteints. Arrêt.")
                exit(1)
            else:
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Erreur inattendue lors de la connexion à RabbitMQ : {e}")
            traceback.print_exc()
            exit(1)

def fetch_and_send_rss_feeds(channel):
    rss_feeds = [
        "https://fr.cointelegraph.com/rss",
        "https://www.bfmtv.com/rss/crypto/"
    ]

    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            image_url = get_image_url(entry)
            message = {
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'summary': entry.summary,
                'source': feed_url,
                'image_url': image_url
            }
            send_to_rabbitmq(message, channel)


def get_image_url(entry):
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    elif 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0]['url']
    elif 'image' in entry:
        return entry.image.href
    elif 'enclosure' in entry:
        return entry.enclosure.get('url')
    else:
        # Essayer de parser le champ description pour trouver une image
        description = entry.get('description', '')
        if description:
            soup = BeautifulSoup(description, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'):
                return img['src']
        return None

def send_to_rabbitmq(message, channel):
    try:
        #message_str = json.dumps(message)
        result = collection.insert_one(message)
        message_id = str(result.inserted_id)

        channel.basic_publish(
            exchange="", # On envoie directement à la queue
            routing_key=QUEUE_NAME,
            #body=message_str,
            body=message_id,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        #print(f"Message envoyé à RabbitMQ : {message['title']}")
        print(f"Message ID envoyé à RabbitMQ : {message_id}")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message à RabbitMQ : {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        while True:
            print(f"Début de la collecte des flux RSS à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            connection = connect_to_rabbitmq()
            channel = connection.channel()
            
            # Déclarer la queue dédiée avec un DLX (Dead Letter Exchange) pour les messages non traités
            args = {
                "x-dead-letter-exchange": "dlx_news_feed", 
                "x-message-ttl": 60000 
            }
            channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)

            fetch_and_send_rss_feeds(channel)
            connection.close()
            print(f"Fin de la collecte. Attente avant la prochaine collecte...")
            time.sleep(600)  # 600 sec (10 mins)
    except KeyboardInterrupt:
        print("Arrêt du producteur RSS.")