#!/usr/bin/env python
# coding: utf-8

import mlflow
import mlflow.xgboost
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
import pandas as pd


# Set MLflow tracking URI
EC2_PUBLIC_DNS='ec2-16-16-217-131.eu-north-1.compute.amazonaws.com'
mlflow.set_tracking_uri(f"http://{EC2_PUBLIC_DNS}:5000")

# Set experiment name
mlflow.set_experiment("xgboost_optimized_model")

# Load the cleaned data
cleaned_df = pd.read_csv('../data/cleaned_car_data.csv')

# Define features (X) and target variable (y)
X = cleaned_df.drop(columns=['price'])
y = cleaned_df['price']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Optimized hyperparameters from hyperopt
params = {
    'learning_rate': 0.09455111298980684,
    'max_depth': int(9.0),
    'min_child_weight': 0.3730492049381335,
    'n_estimators': int(500.0),
    'subsample': 0.9989341273723211,
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse'
}

# Start an MLflow run
with mlflow.start_run():
    # Initialize and train the model
    model = xgb.XGBRegressor(**params)
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Calculate metrics
    rmse = root_mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Log parameters and metrics
    mlflow.log_params(params)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("r2_score", r2)

    # Log the model
    signature = ms.infer_signature(X_train, y_train)
    input_example = X_train[:1]
    mlflow.xgboost.log_model(model, artifact_path="xgboost_model", signature=signature, input_example=input_example)

    print(f"RMSE: {rmse}, MAE: {mae}, R2 Score: {r2}")
