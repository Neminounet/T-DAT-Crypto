import pika
import os
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from data_functions import save_price_message

# Configuration de RabbitMQ
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', '/')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'admin')

QUEUE_NAME = 'historical_price_queue_error'

# Configuration de MongoDB
MONGODB_HOST = os.environ.get('MONGODB_HOST', 'mongodb')
MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
MONGO_ROOT_USER = os.environ.get('MONGO_ROOT_USER', 'root')
MONGO_ROOT_PASSWORD = os.environ.get('MONGO_ROOT_PASS', 'root')

client = MongoClient(
    host=MONGODB_HOST,
    port=MONGODB_PORT,
    username=MONGO_ROOT_USER,
    password=MONGO_ROOT_PASSWORD,
)
db = client['crypto_db']
collection = db['historical_prices']
failed_collection = db['failed_historical_prices']

# Connexion à RabbitMQ
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

MAX_RETRIES = 3  # Nombre maximum de tentatives

# Fonction de callback
def on_message_received(ch, method, properties, body):
    message_id = body.decode()
    headers = properties.headers or {}
    retry_count = headers.get('x-retry-count', 0)
    print(f"Message ID reçu depuis le DLX : {message_id}, tentative n°{retry_count + 1}")
    try:
        # Récupérer le message depuis MongoDB
        document = collection.find_one({'_id': ObjectId(message_id)})
        if document:
            # Tenter de retraiter le message
            save_price_message(document)
            # Supprimer le document de MongoDB
            collection.delete_one({'_id': ObjectId(message_id)})
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("Message retraité avec succès")
        else:
            print("Message introuvable dans MongoDB.")
            # Acquitter le message pour le retirer de la queue DLX
            ch.basic_ack(delivery_tag=method.delivery_tag)
            # Vous pouvez enregistrer ce cas pour une analyse ultérieure
    except Exception as e:
        print(f"Erreur lors du retraitement du message : {e}")
        if retry_count < MAX_RETRIES - 1:
            # Incrémenter le compteur de tentatives
            headers['x-retry-count'] = retry_count + 1
            # Republier le message dans la même queue pour une nouvelle tentative
            ch.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=body,
                properties=pika.BasicProperties(
                    headers=headers,
                    delivery_mode=2  # Pour rendre le message persistant
                )
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Message réenquêté pour une nouvelle tentative (tentative n°{retry_count + 1})")
        else:
            # Nombre maximum de tentatives atteint
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("Nombre maximum de tentatives atteint, le message est marqué comme définitivement échoué.")
            # Enregistrer le message pour analyse ultérieure
            failed_collection.insert_one({
                'message_id': message_id,
                'error': str(e),
                'document': document,
                'retry_count': retry_count + 1
            })
            collection.delete_one({'_id': ObjectId(message_id)})

channel.queue_declare(queue=QUEUE_NAME, durable=True)

channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=on_message_received
)

print("Start consuming DLX historical price messages")
channel.start_consuming()