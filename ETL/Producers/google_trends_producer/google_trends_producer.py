from pytrends.request import TrendReq # pip install pytrends
from pymongo import MongoClient # pip install pymongo
import pika # pip install pika
import traceback
import json
import time
import os

# Configuration de pytrends
pytrends = TrendReq(hl="fr-FR", tz=360)

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

QUEUE_NAME = "google_trends_queue"

# Connexion à MongoDB
client = MongoClient(
    host=MONGODB_HOST, 
    port=MONGODB_PORT,
    username=MONGO_ROOT_USER,
    password=MONGO_ROOT_PASSWORD,
)
db = client["crypto_db"]
collection = db["google_trends"]

def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials)
    max_retries = 10
    retry_delay = 5 

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

def fetch_and_send_google_trends(keywords):
    pytrends.build_payload(keywords, cat=0, timeframe='now 1-H', geo='', gprop='')
    data = pytrends.interest_over_time()
    if not data.empty:
        # Faut convertir l'index en colonne pour pouvoir le sérialiser en JSON
        data.reset_index(inplace=True)
        data_dict = data.to_dict(orient="records") # orient = "records" pour avoir une liste de dictionnaires
        # Insérer dans MongoDB
        result = collection.insert_one({'data': data_dict})
        message_id = str(result.inserted_id)
        # Envoyer l'identifiant via RabbitMQ
        send_to_rabbitmq(message_id)
        
    else: 
        print("Aucune donnée trouvée :(")

def send_to_rabbitmq(message_id):
    try:
        channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=message_id,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        print(f"Message ID envoyé à RabbitMQ : {message_id}")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message à RabbitMQ : {e}")

if __name__ == "__main__":
    try:
        while True:
            connection = connect_to_rabbitmq()
            channel = connection.channel()
            args = {
                    'x-dead-letter-exchange': 'dlx_google_trends',
                    'x-message-ttl': 60000
                }

            channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)

            keywords = ["bitcoin", "ethereum", "Litecoin"]
            fetch_and_send_google_trends(keywords)

            connection.close()
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Arrêt du producteur Google Trends.")
