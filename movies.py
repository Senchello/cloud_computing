from flask import Flask, jsonify, request
from werkzeug.exceptions import NotFound
import boto3
from botocore.exceptions import ClientError
import logging
import json
from prometheus_flask_exporter import PrometheusMetrics

# Ініціалізація Flask та Prometheus
app = Flask(__name__)
metrics = PrometheusMetrics(app)  # Підключення Prometheus Exporter

# Ініціалізація DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('Movies')

# Ініціалізація логування (структуровані логи)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def log_info(message, **kwargs):
    log_data = {"level": "INFO", "message": message}
    log_data.update(kwargs)
    logger.info(json.dumps(log_data))

def log_error(message, **kwargs):
    log_data = {"level": "ERROR", "message": message}
    log_data.update(kwargs)
    logger.error(json.dumps(log_data))

# Функція для отримання всіх фільмів
@app.route("/movies", methods=['GET'])
def movie_record():
    log_info("Request to fetch all movies", client_ip=request.remote_addr)
    try:
        response = table.scan()
        return jsonify(response.get('Items', []))
    except ClientError as e:
        log_error("Error fetching movies", error=e.response['Error']['Message'])
        return jsonify({"error": "Failed to fetch movies"}), 500

# Головна сторінка API
@app.route("/", methods=['GET'])
def hello():
    log_info("Root endpoint accessed", client_ip=request.remote_addr)
    return jsonify({"uri": "/", "movies": "/movies"})

if __name__ == "__main__":
    log_info("Starting Movies Service", port=5001)
    app.run(host="0.0.0.0", port=5001)
