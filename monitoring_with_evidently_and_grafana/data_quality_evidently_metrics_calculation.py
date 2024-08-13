import datetime
import os
import time
import logging
import pandas as pd
import psycopg
import mlflow.pyfunc
from mlflow.artifacts import download_artifacts
from prefect import task, flow
from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10  # Time to wait between sending metrics

# SQL to create the necessary table for metrics
create_table_statement = """
DROP TABLE IF EXISTS car_metrics;
CREATE TABLE car_metrics(
    timestamp TIMESTAMP,
    prediction_drift FLOAT,
    num_drifted_columns integer,
    share_missing_values FLOAT
)
"""

# Load the ML model from MLflow
@task
def load_model():
    from dotenv import load_dotenv
    # Set AWS credentials as environment variables
    load_dotenv()

    EC2_PUBLIC_DNS = 'ec2-16-16-217-131.eu-north-1.compute.amazonaws.com'
    MLFLOW_TRACKING_URI = f"http://{EC2_PUBLIC_DNS}:5000"
    RUN_ID = '9c4533e2d8c049fdae991d4ba055ff38'
    MODEL_PATH = 'xgboost_model'

    dst_path = './'

    # Download the artifacts from S3 via MLflow
    model_path = download_artifacts(run_id=RUN_ID, artifact_path=MODEL_PATH, tracking_uri=MLFLOW_TRACKING_URI, dst_path=dst_path)

    logged_model = './xgboost_model'
    model = mlflow.pyfunc.load_model(logged_model)
    return model



# Load reference data
reference_data = pd.read_csv('../data/cleaned_car_data.csv')

# Define features
num_features = ['year', 'mileage', 'enginesize', 'tax', 'mpg']
cat_features = ['make_bmw', 'make_cclass', 'make_focus', 'make_ford', 'make_hyundi', 'make_merc', 'make_skoda', 'make_toyota', 'make_vauxhall', 'make_vw', 'transmission_Manual', 'transmission_Semi-Auto', 'fueltype_Hybrid', 'fueltype_Petrol']

column_mapping = ColumnMapping(
    prediction='price',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None
)

report = Report(metrics=[
    ColumnDriftMetric(column_name='price'),  # Monitor drift in the predicted price
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])

@task
def prep_db():
    with psycopg.connect("host=localhost port=5432 user=postgres password=example", autocommit=True) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("CREATE DATABASE test;")
        with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn:
            conn.execute(create_table_statement)

@task
def calculate_metrics_postgresql(model):
    current_data = pd.read_csv('../data/cleaned_car_data.csv')  # Use the single cleaned file
    current_data['price'] = model.predict(current_data[num_features + cat_features].fillna(0))

    report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
    result = report.as_dict()

    # Print the result to debug
    logging.info(f"Report result: {result}")

    # Check available keys
    metrics = result.get('metrics', [])
    for metric in metrics:
        logging.info(f"Metric name: {metric.get('name')}, Metric result: {metric.get('result')}")

    # Extract metrics based on available keys
    try:
        metrics = result.get('metrics', [])

        # Iterate over metrics to find and extract values
        for metric in metrics:
            metric_name = metric.get('metric')
            metric_result = metric.get('result', {})

            if metric_name == 'ColumnDriftMetric':
                prediction_drift = metric_result.get('drift_score')
            elif metric_name == 'DatasetDriftMetric':
                num_drifted_columns = metric_result.get('number_of_drifted_columns')
            elif metric_name == 'DatasetMissingValuesMetric':
                share_missing_values = metric_result.get('share_of_missing_values')
    except KeyError as e:
        logging.error(f"KeyError: {e}")
        raise

    with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
        with conn.cursor() as curr:
            curr.execute(
                "INSERT INTO car_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) VALUES (%s, %s, %s, %s)",
                (datetime.datetime.now(), prediction_drift, num_drifted_columns, share_missing_values)
            )

@flow
def batch_monitoring_backfill():
    model = load_model()
    prep_db()
    calculate_metrics_postgresql(model)

if __name__ == '__main__':
    batch_monitoring_backfill()
