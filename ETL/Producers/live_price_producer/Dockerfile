# Utiliser une image Python légère
FROM python:3.12-slim

# Définir le répertoire de travail dans le container
WORKDIR /app

# Copier les fichiers nécessaires pour l'application producteur
COPY ETL/Producers/live_price_producer .

# Installer les dépendances spécifiques au producteur
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script 'wait_for_it.sh' pour attendre le démarrage de RabbitMQ et MongoDB
COPY ETL/wait_for_it .

# Donner les droits d'exécution au script 'wait_for_it.sh'
RUN chmod +x ./wait-for-it.sh

# Définir la commande à exécuter lorsque le container démarre
CMD ["./wait-for-it.sh", "rabbitmq:5672", "--", "./wait-for-it.sh", "mongodb:27017", "--", "python", "live_price_producer.py"]
