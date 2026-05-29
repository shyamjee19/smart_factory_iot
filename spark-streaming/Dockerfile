FROM bitnami/spark:3.5.0
USER root
RUN apt-get update && apt-get install -y python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
# Download postgres JDBC driver
RUN mkdir -p /opt/bitnami/spark/jars/ && \
    curl -o /opt/bitnami/spark/jars/postgresql-42.6.0.jar https://jdbc.postgresql.org/download/postgresql-42.6.0.jar
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", "stream_processor.py"]
