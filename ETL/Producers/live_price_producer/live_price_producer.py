import json
import websocket # pip install websocket-client
from pymongo import MongoClient # pip install pymongo
from datetime import datetime
import requests # pip install requests
import time
import os
import pika # pip install pika

# Configuration de MongoDB
MONGODB_HOST = os.environ.get('MONGODB_HOST', 'mongodb')
MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
MONGO_ROOT_USER = os.environ.get('MONGO_ROOT_USER', 'root')
MONGO_ROOT_PASSWORD = os.environ.get('MONGO_ROOT_PASS', 'root')

# Configuration de la connexion à RabbitMQ
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', '/')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'admin')

# Nome de la queue dédiée : 
QUEUE_NAME = "live_price_queue"

# Connexion à MongoDB
client = MongoClient(
    host=MONGODB_HOST, 
    port=MONGODB_PORT,
    username=MONGO_ROOT_USER,
    password=MONGO_ROOT_PASSWORD,
)
db = client["crypto_db"]
collection = db["live_prices"]

assets = ["BTCEUR", "ETHEUR", "BNBEUR", "SOLEUR", "XRPEUR", "ADAEUR", "DOGEEUR", "LTCEUR", "XLMEUR", "TRXEUR"]
# Alors niveau intervalles de temps, on a le choix entre 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
# 1m semble être le plus précis, mais si on veut moins de données ou si on s'approche trop de la limite de requêtes, on peut augmenter l'intervalle
lower_assets = [f"{coin.lower()}@kline_5m" for coin in assets]
joined_assets = "/".join(lower_assets)

# On fait des requêtes pour obtenir les prix initiaux
# Car certains assets ne se mettent pas à jour fréquemment et donc on ne recevra pas de message pour eux
def get_initial_prices(assets):
    prices = []
    for asset in assets:
        current_asset = {}
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={asset}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_asset["asset"] = asset
            current_asset["price"] = data['price']
            current_asset["event_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            prices.append(current_asset)
           # prices[asset] = data['price']
        else:
            current_asset["asset"] = asset
            current_asset["price"] = None
            current_asset["event_time"] = None
            # prices[asset] = None
    return prices

def format_message(message):
    return {
        "event_time": datetime.fromtimestamp(int(message["data"]["E"]) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
        "asset": message["data"]["s"],
        "price": message["data"]['k']['c'],
    }

def send_to_rabbitmq(message):
    try:
        result = collection.insert_one(message)
        message_id = str(result.inserted_id)

        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Déclarer la queue dédiée avec un DLX (Dead Letter Exchange) pour les messages non traités
        args = {
            "x-dead-letter-exchange": "dlx_live_price", # DLX pour les messages non traités de cette queue
            "x-message-ttl": 60000 # C'est à dire que les messages non traités seront redirigés après 60 secondes vers le DLX
         }

        # Déclarer la queue dédiée avec les arguments : 
        # durable=True pour que la queue survive à un redémarrage du serveur RabbitMQ
        # arguments=args pour les arguments définis plus haut
        channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args) 

        # Envoyer le message directement à la queue dédiée
        # message_str = json.dumps(message) # Convertir le message en JSON pour l'envoyer à RabbitMQ

        channel.basic_publish(
            exchange="", # Pas besoin d'échange pour envoyer directement à la queue
            routing_key=QUEUE_NAME, # Nom de la queue dédiée
            #body=message_str, # Message à envoyer
            body=message_id, # On envoie l'ID du message dans la collection MongoDB
            properties=pika.BasicProperties(delivery_mode=2) # delivery_mode=2 pour que le message survive à un redémarrage du serveur RabbitMQ
        )
        #print(f"Message envoyé à RabbitMQ : {message_str}")
        print(f"Message ID envoyé à RabbitMQ : {message_id}")
        connection.close()
    except Exception as e:
        print(f"Erreur lors de l'envoi du message à RabbitMQ : {e}")

def on_message(ws, message):
    try: 
        message = json.loads(message)
        formatted_message = format_message(message)
        print(f"Reçu par le WebSocket : {formatted_message}")
        send_to_rabbitmq(formatted_message)
    except Exception as e:
        print(f"Erreur lors du traitement du message webScoket : {e}")

def on_error(ws, error):
    print(f"Erreur : {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connexion fermée")
    print(f"Code : {close_status_code}, Message : {close_msg}")
    time.sleep(5)  # Attendre 5 secondes avant de se reconnecter pour éviter d'être ejecté par le serveur :/ 
    reconnect()

def on_open(ws):
    print("Connexion ouverte")

def start_socket():
    socket = f"wss://stream.binance.com:9443/stream?streams={joined_assets}"
    ws = websocket.WebSocketApp(
        url=socket,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.run_forever()

def reconnect():
    print("Tentative de reconnexion au webSocket... :O")
    start_socket()

if __name__ == "__main__":
    # Obtenir les prix de chaque asset avant le websocket
    initial_prices = get_initial_prices(assets)
    print("Prix initiaux :", initial_prices)
    # Envoyer les prix initiaux à RabbitMQ
    for price in initial_prices:
        send_to_rabbitmq(price)
    # Démarrer le WebSocket
    start_socket()

