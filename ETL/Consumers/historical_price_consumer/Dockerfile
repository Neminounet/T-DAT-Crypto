FROM python:3.12-slim

WORKDIR /app

# Copier le package 'common' et l'installer
COPY ETL/Consumers/common ./common
RUN pip install /app/common

# Installer les fichiers nécessaires pour l'application consommateur
COPY ETL/Consumers/historical_price_consumer .

# Installer les dépendances spécifiques au consommateur
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script 'wait_for_it.sh' pour attendre le démarrage de RabbitMQ et MongoDB
COPY ETL/wait_for_it .

# Donner les droits d'exécution au script 'wait_for_it.sh'
RUN chmod +x ./wait-for-it.sh

# Exécuter l'application consommateur
CMD ["./wait-for-it.sh", "rabbitmq:5672", "--", "./wait-for-it.sh", "mongodb:27017", "--", "./wait-for-it.sh", "timescaledb:5432", "--", "python", "-u", "historical_price_consumer.py"]


