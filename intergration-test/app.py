from flask import Flask, request, jsonify
import mlflow.pyfunc
import pandas as pd

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
