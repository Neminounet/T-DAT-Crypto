# db_initializer/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY ETL/Consumers/common ./common
RUN pip install /app/common

COPY ETL/Consumers/db_initializer .

COPY ETL/wait_for_it .
RUN chmod +x ./wait-for-it.sh

CMD ["./wait-for-it.sh", "timescaledb:5432", "--","python", "-u", "db_initializer.py"]
