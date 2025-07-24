from pymongo import MongoClient
from bson.objectid import ObjectId
from common.db_config import pg_db
from common.models.trends_data import TrendsData
from data_functions import save_trends_data
import pika
import os
import json
import time

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

QUEUE_NAME = 'google_trends_queue'

# Connexion à MongoDB
client = MongoClient(
    host=MONGODB_HOST, 
    port=MONGODB_PORT,
    username=MONGO_ROOT_USER,
    password=MONGO_ROOT_PASSWORD,
)
db = client["crypto_db"]
collection = db["google_trends"]

# Connexion à RabbitMQ
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials)

# Boucle de tentative de connexion
max_retries = 10
retry_delay = 5  # secondes

for attempt in range(1, max_retries + 1):
    try:
        print(f"Attempt {attempt}/{max_retries}: Connecting to RabbitMQ...")
        connection = pika.BlockingConnection(parameters)
        print("Connected to RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError as error:
        print(f"Connection attempt {attempt} failed: {error}")
        if attempt == max_retries:
            print("Max retries reached. Exiting.")
            exit(1)
        else:
            time.sleep(retry_delay)
else:
    print("Unable to connect to RabbitMQ. Exiting.")
    exit(1)

channel = connection.channel()

# Déclarer l'exchange DLX
channel.exchange_declare(exchange='dlx_google_trends', exchange_type='fanout', durable=True)

# Déclarer la queue d'erreur et la lier à l'exchange DLX
channel.queue_declare(queue='google_trends_queue_error', durable=True)
channel.queue_bind(exchange='dlx_google_trends', queue='google_trends_queue_error')

# Déclarer la queue principale avec les arguments pour DLX
args = {
    'x-dead-letter-exchange': 'dlx_google_trends',
    'x-message-ttl': 60000
}
channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)


def on_message_received(ch, method, properties, body):
    message_id = body.decode()
    print(f"Message ID reçu : {message_id}")
    try:
        # Récupérer le message depuis MongoDB
        document = collection.find_one({'_id': ObjectId(message_id)})
        if document:
            data = document['data']  # Liste de dictionnaires
            # Traiter les données
            save_trends_data(data)
            # Supprimer le document de MongoDB
            collection.delete_one({'_id': ObjectId(message_id)})
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("Données Google Trends introuvables.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"Erreur lors du traitement des données : {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=on_message_received
)

print("Start consuming google trends data...")
channel.start_consuming()