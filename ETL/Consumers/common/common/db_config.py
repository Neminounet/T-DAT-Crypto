from peewee import PostgresqlDatabase, Model, OperationalError
import os

pg_db = PostgresqlDatabase(
    os.environ.get('DB_NAME', 'your_database'),
    host=os.environ.get('DB_HOST', 'timescaledb'),
    user=os.environ.get('DB_USER', 'postgres'),
    password=os.environ.get('DB_PASSWORD', 'postgres'),
    port=int(os.environ.get('DB_PORT', 5432))
)

class BaseModel(Model):
    class Meta:
        database = pg_db

import time

def initialize_db():
    from common.models.price_data import PriceData
    from common.models.news_data import NewsData
    from common.models.trends_data import TrendsData
    max_retries = 10
    retry_delay = 5  # c'est en secondes

    for attempt in range(1, max_retries + 1):
        try:
            with pg_db:
                pg_db.create_tables([PriceData, NewsData, TrendsData], safe=True)

                # Créer l'hypertable avec chunk_time_interval
                pg_db.execute_sql("""
                    SELECT create_hypertable('price_data', 'timestamp', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);
                """)

                pg_db.execute_sql("""
                    SELECT create_hypertable('trends_data', 'timestamp', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);
                """)

                # Ajouter la politique de rétention
                pg_db.execute_sql("""
                    SELECT add_retention_policy('price_data', INTERVAL '2 years', if_not_exists => TRUE);
                """)

               # Vérifier si la compression est déjà activée
                compression_enabled = pg_db.execute_sql("""
                    SELECT count(*)
                    FROM _timescaledb_catalog.hypertable
                    WHERE table_name = 'price_data' AND compression_state = 2;
                """).fetchone()[0]

                if compression_enabled == 0:
                    # Activer la compression sur l'hypertable
                    pg_db.execute_sql("""
                        ALTER TABLE price_data SET (
                            timescaledb.compress,
                            timescaledb.compress_segmentby = 'asset'
                        );
                    """)

            # Ajouter une politique de compression pour compresser les chunks plus anciens que 7 jours
            pg_db.execute_sql("""
                SELECT add_compression_policy('price_data', INTERVAL '7 days', if_not_exists => TRUE);
            """)

            print("Base de données initialisée avec succès.")
            break
        except OperationalError as e:
            print(f"Attempt {attempt}/{max_retries}: Erreur lors de l'initialisation de la base de données : {e}")
            if attempt == max_retries:
                print("Max retries atteints. Arrêt.")
                exit(1)
            else:
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            exit(1)



