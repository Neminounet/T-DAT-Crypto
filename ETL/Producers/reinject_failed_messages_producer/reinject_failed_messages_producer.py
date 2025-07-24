from pymongo import MongoClient
from bson.objectid import ObjectId
import pika
import os

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

# Configuration de RabbitMQ
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', '/')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'admin')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

def declare_queue(queue_name):
    # Dans le nom des dlx, il n'y a pas de _queue... 
    args = {
        'x-dead-letter-exchange': f'dlx_{queue_name}',
        'x-message-ttl': 60000  
    }

    # Ajouter _queue à la queue_name :o
    queue_name = f'{queue_name}_queue'

    channel.queue_declare(queue=queue_name, durable=True, arguments=args)
    print(f"Queue : {queue_name}  => déclarée avec succès")

def reinject_failed_messages(collection_name, queue_name):
    # Check si la collec existe dans la DB :
    if collection_name not in db.list_collection_names():
        print(f"La collection {collection_name} n'existe pas.")
        return

    failed_collection = db[collection_name]
    messages = list(failed_collection.find())

    if not messages:
        print(f"Aucun message à réinjecter pour la collection {collection_name}")
        return

    # Déclarer la queue / DLX
    declare_queue(queue_name)

    # Ajouter _queue à la queue_name, pour les même raisons que ci-dessus :D
    queue_name = f'{queue_name}_queue'


    for message in messages:
        message_id = message['message_id']
        headers = {'x-retry-count': 0} 

        # Publier le message ID dans la queue principale
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message_id,
            properties=pika.BasicProperties(
                headers=headers,
                delivery_mode=2 
            )
        )
        print(f"Réinjection du message ID {message_id} dans la queue {queue_name}")

        # Supprimer le message de la collection failed
        failed_collection.delete_one({'_id': message['_id']})


if __name__ == "__main__":
    try: 
        # Réinjecter les messages pour live_price
        reinject_failed_messages('failed_live_prices', 'live_price')

        # Réinjecter les messages pour historical_prices
        reinject_failed_messages('failed_historical_prices', 'historical_prices')

        # Réinjecter les messages pour news_feed
        reinject_failed_messages('failed_news_feed', 'news_feed')

        # Réinjecter les messages pour google_trends
        reinject_failed_messages('failed_google_trends', 'google_trends')
    except Exception as e:
        print(f"Erreur lors de la réinjection : {e}")

    connection.close()
    print("Fin de la réinjection des messages")

