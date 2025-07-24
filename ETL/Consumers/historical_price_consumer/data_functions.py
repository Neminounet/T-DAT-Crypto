from common.db_config import pg_db
from common.models.price_data import PriceData
from datetime import datetime

def save_price_message(message):
    timestamp_str = message.get('event_time')
    asset = message.get('asset')
    price_str = message.get('price') 

    # Vérifier que l'on a toutes les donénes 
    if timestamp_str is None or asset is None or price_str is None:
        raise ValueError("Le message ne contient pas toutes les données requises.")

    # Conversion des données
    try:
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        raise ValueError(f"Format de date invalide : {e}")

    try:
        price = float(price_str)
    except ValueError as e:
        raise ValueError(f"Impossible de convertir le prix en float : {e}")

    # Insérer les données dans la BDD !
    try:
        with pg_db.atomic():
            PriceData.create(
                timestamp=timestamp,
                asset=asset,
                price=price
            )
    except Exception as e:
        print(f"Erreur lors de l'insertion dans la base de données : {e}")
        raise e

