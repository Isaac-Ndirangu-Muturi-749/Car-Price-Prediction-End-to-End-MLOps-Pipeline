from flask import Flask, request, jsonify
import mlflow.pyfunc
import pandas as pd
import os
from mlflow.artifacts import download_artifacts
from dotenv import load_dotenv

# Set AWS credentials as environment variables
load_dotenv()

# EC2 Public DNS and MLflow tracking URI
EC2_PUBLIC_DNS = 'ec2-16-16-217-131.eu-north-1.compute.amazonaws.com'
MLFLOW_TRACKING_URI = f"http://{EC2_PUBLIC_DNS}:5000"
RUN_ID = '9c4533e2d8c049fdae991d4ba055ff38'
MODEL_PATH = 'xgboost_model'

# Define the destination path (current directory)
dst_path = './'

# Download the artifacts from S3 via MLflow
model_path = download_artifacts(run_id=RUN_ID, artifact_path=MODEL_PATH, tracking_uri=MLFLOW_TRACKING_URI, dst_path=dst_path)

print(f"Artifacts downloaded in: {model_path}")
print(f"Content: {os.listdir(model_path)}")

# Load the model
logged_model = './xgboost_model'
loaded_model = mlflow.pyfunc.load_model(logged_model)

# Initialize the Flask app
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Get JSON data from request
    data = request.get_json(force=True)

    # Convert data to DataFrame
    df = pd.DataFrame([data])

    # Predict using the model
    predictions = loaded_model.predict(df)

    # Return the predictions as JSON
    return jsonify(predictions.tolist())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
