import os
import json
import mlflow


def get_model_location(run_id):
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return model_location

    model_bucket = os.getenv('MODEL_BUCKET', 'mlflow-artifacts-capstone-mlops')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID', '5')

    model_location = f's3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model'
    return model_location


def load_model(run_id):
    model_path = get_model_location(run_id)
    model = mlflow.pyfunc.load_model(model_path)
    return model


class ModelService:
    def __init__(self, model, model_version=None):
        self.model = model
        self.model_version = model_version

    def prepare_features(self, car_data):
        # Assuming car_data is a dictionary with keys as feature names
        return pd.DataFrame([car_data])  # Convert to DataFrame for ML model input

    def predict(self, features):
        pred = self.model.predict(features)
        return float(pred[0])

    def predict_car_price(self, car_data):
        # Prepare features
        features = self.prepare_features(car_data)

        # Predict car price
        prediction = self.predict(features)

        # Return the prediction in a structured way
        return {
            'model': 'car_price_prediction_model',
            'version': self.model_version,
            'prediction': {'car_price': prediction}
        }


# Example usage:
def init(run_id: str):
    # Load the model with the given run_id
    model = load_model(run_id)

    # Create and return the ModelService instance
    model_service = ModelService(model=model, model_version=run_id)

    return model_service
