import pika
import os
import json
import time
from pymongo import MongoClient
from bson import ObjectId
from data_functions import save_price_message

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

QUEUE_NAME = 'historical_price_queue'

# Connexion à MongoDB
client = MongoClient(
    host=MONGODB_HOST, 
    port=MONGODB_PORT,
    username=MONGO_ROOT_USER,
    password=MONGO_ROOT_PASSWORD,
)
db = client["crypto_db"]
collection = db["historical_prices"]

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
channel.exchange_declare(exchange='dlx_historical_price', exchange_type='fanout', durable=True)

# Déclarer la queue d'erreur et la lier à l'exchange DLX
channel.queue_declare(queue='historical_price_queue_error', durable=True)
channel.queue_bind(exchange='dlx_historical_price', queue='historical_price_queue_error')

# Déclarer la queue principale avec les arguments pour DLX
args = {
    'x-dead-letter-exchange': 'dlx_historical_price',
    'x-message-ttl': 60000
}
channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)

# Fonction de callback pour la réception des messages
def on_message_received(ch, method, properties, body):
    #message = json.loads(body)
    #print(f"Message reçu : {message}")

    #try:
       # save_price_message(message)
        #ch.basic_ack(delivery_tag=method.delivery_tag)
    #except Exception as e:
        #print(f"Erreur lors du traitement du message : {e}")
        #ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Rejeter le message sans le remettre dans la queue...
    message_id = body.decode()
    print(f"Message ID reçu : {message_id}")

    try:
        # Récup le message dans la collection mongoDB
        message = collection.find_one({"_id": ObjectId(message_id)})
        if message:
            save_price_message(message)
            collection.delete_one({"_id": ObjectId(message_id)}) # On delete le message de la collection
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f"Message ID {message_id} non trouvé dans la collection")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"Erreur lors du traitement du message : {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=on_message_received
)

print("Start consuming historical prices")
channel.start_consuming()
