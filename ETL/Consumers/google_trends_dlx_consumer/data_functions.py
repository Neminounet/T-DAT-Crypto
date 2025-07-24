from common.models.trends_data import TrendsData
from common.db_config import pg_db
from datetime import datetime

def save_trends_data(data):
    try: 
        with pg_db.atomic():
            records = []
            for item in data:
                # Extraire l'horodatage
                timestamp = item['date']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                is_partial = item.get('isPartial', False)
                # Parcourir les mots-clés
                for keyword in ['bitcoin', 'ethereum', 'Litecoin']:
                    interest = item.get(keyword, None)
                    if interest is not None:
                        record = {
                            'timestamp': timestamp,
                            'keyword': keyword,
                            'interest': interest,
                            'is_partial': is_partial
                        }
                        records.append(record)
            # Insérer les enregistrements en une seule transaction
            if records:
                TrendsData.insert_many(records).on_conflict_ignore().execute()
    except Exception as e:
        print(f"Erreur lors de l'insertion dans la base de données : {e}")
        raise e
