import os
import pika
import requests
import json
from datetime import datetime
from pymongo import MongoClient
import time
import traceback
import os 

# Configuration MongoDB
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

QUEUE_NAME = "historical_price_queue"

# Connexion à MongoDB
client = MongoClient(
    host=MONGODB_HOST, 
    port=MONGODB_PORT,
    username=MONGO_ROOT_USER,
    password=MONGO_ROOT_PASSWORD,
)
db = client["crypto_db"]
collection = db["historical_prices"]

# Liste des actifs
assets = ["BTCEUR", "ETHEUR", "BNBEUR", "SOLEUR", "XRPEUR", "ADAEUR", "DOGEEUR", "LTCEUR", "XLMEUR", "TRXEUR"]

def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials)
    max_retries = 10
    retry_delay = 5  # secondes

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

def get_historical_prices(assets, channel):
    for asset in assets:
        print(f"Récupération des données pour {asset}")
        base_url = "https://api.binance.com/api/v3/klines"
        interval = "1d"
        limit = 365

        params = {
            "symbol": asset,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        for kline in data:
            message = {
                "event_time": datetime.fromtimestamp(int(kline[0]) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "asset": asset,
                "price": kline[4]
            }
            send_to_rabbitmq(message, channel)

def send_to_rabbitmq(message, channel):
    try:
        # message_str = json.dumps(message)
        result = collection.insert_one(message)
        message_id = str(result.inserted_id)

        channel.basic_publish(
            exchange="", # On envoie directement à la queue
            routing_key=QUEUE_NAME,
            # body=message_str,
            body=message_id,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        # print(f"Message envoyé à RabbitMQ : {message_str}")
        print(f"Message envoyé à RabbitMQ : {message_id}")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message à RabbitMQ : {e}")
        traceback.print_exc()

def historical_data_already_loaded():
    return os.path.exists('/data/historical_data_loaded.txt')

def mark_historical_data_as_loaded():
    with open('/data/historical_data_loaded.txt', 'w') as f:
        f.write('Data loaded')

if __name__ == "__main__":
    if historical_data_already_loaded():
        print("Données historiques déjà chargées")
        exit(0)
    else:
        print("Début de la récupération des données historiques")
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        
        args = {
            "x-dead-letter-exchange": "dlx_historical_price",
            "x-message-ttl": 60000
        }

        channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)

        get_historical_prices(assets, channel)
        connection.close()
        print("Fin de la récupération des données historiques")
        mark_historical_data_as_loaded()
