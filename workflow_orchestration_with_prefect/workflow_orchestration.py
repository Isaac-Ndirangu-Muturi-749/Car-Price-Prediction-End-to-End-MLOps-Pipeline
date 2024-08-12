#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import numpy as np
from prefect import flow, task
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import mlflow
import mlflow.xgboost

# --- Data Preprocessing and Cleaning Tasks ---

def standardize_columns(df):
    df.columns = [col.lower().replace(' ', '_').replace('£', '') for col in df.columns]
    return df

def clean_data(df):
    df = df.dropna()
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['price'] = df['price'].replace('[£,]', '', regex=True).astype(float)
    if 'tax' in df.columns:
        df['tax'] = df['tax'].replace('[£,]', '', regex=True).astype(float)
    if 'tax_' in df.columns:
        df['tax_'] = df['tax_'].replace('[£,]', '', regex=True).astype(float)
    return df

# Define a function to extract make from filename
def extract_make(filename):
    return filename.split('.')[0]

@task
def load_and_process_datasets(data_dir):
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    dataframes = {}
    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        df = standardize_columns(df)
        df['make'] = extract_make(file)
        df = clean_data(df)
        columns = ['make'] + [col for col in df.columns if col != 'make']
        df = df[columns]
        dataframes[file] = df
        print(f"--- {file} ---")
        print(df.head())
        print("\n")
    return dataframes

@task
def combine_datasets(dataframes):
    combined_df = pd.concat(dataframes.values(), ignore_index=True)
    return combined_df

@task
def drop_redundant_columns(df):
    columns_to_drop = ['tax()', 'fuel_type', 'engine_size', 'mileage2', 'fuel_type2', 'engine_size2', 'reference']
    df = df.drop(columns=columns_to_drop, errors='ignore')
    return df

@task
def handle_unclean_categories(df):
    make_mapping = {'unclean focus': 'focus', 'unclean cclass': 'cclass'}
    df['make'] = df['make'].replace(make_mapping)
    return df

@task
def convert_mileage(df):
    df['mileage'] = df['mileage'].replace('[\D]', '', regex=True).astype(float)
    return df

@task
def handle_missing_values(df):
    df['fueltype'] = df['fueltype'].fillna(df['fueltype'].mode()[0])
    df['enginesize'] = df['enginesize'].fillna(df['enginesize'].median())
    df['tax'] = df['tax'].fillna(df['tax'].median())
    df['mpg'] = df['mpg'].fillna(df['mpg'].median())
    return df

@task
def feature_engineering(df):
    df = pd.get_dummies(df, columns=['make', 'transmission', 'fueltype'], drop_first=True)
    return df

@task
def handle_unusual_year_values(df):
    df = df[df['year'].between(1980, 2024)]
    return df

@task
def handle_outliers(df):
    z_scores = np.abs(stats.zscore(df['price'].dropna()))
    df = df[(z_scores < 3)]
    df = df[df['mileage'].astype(float) <= 200000]
    df = df[df['mpg'] <= 100]
    return df

@task
def drop_duplicates(df):
    df = df.drop_duplicates()
    return df

@task
def handle_low_frequency_categories(df):
    df_cleaned = df.drop(columns=['transmission_Other', 'fueltype_Electric', 'fueltype_Other', 'model'], errors='ignore')
    return df_cleaned

@flow
def data_preprocessing_flow(data_dir, combined_output_file, cleaned_output_file):
    # Load, standardize, and clean datasets
    dataframes = load_and_process_datasets(data_dir)
    combined_df = combine_datasets(dataframes)
    combined_df.to_csv(combined_output_file, index=False)
    print(f"Combined dataset saved to '{combined_output_file}'.")

    # Further clean and process the combined dataset
    df = pd.read_csv(combined_output_file)
    df = drop_redundant_columns(df)
    df = handle_unclean_categories(df)
    df = convert_mileage(df)
    df = handle_missing_values(df)
    df = feature_engineering(df)
    df = handle_unusual_year_values(df)
    df = handle_outliers(df)
    df = drop_duplicates(df)
    df = handle_low_frequency_categories(df)

    # Save the cleaned DataFrame to a CSV file
    df.to_csv(cleaned_output_file, index=False)
    print(f"Cleaned dataset saved to '{cleaned_output_file}'.")

# --- Model Training Tasks ---

@task
def setup_mlflow():
    # Set AWS credentials as environment variables
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()

    EC2_PUBLIC_DNS = 'ec2-16-16-217-131.eu-north-1.compute.amazonaws.com'
    mlflow.set_tracking_uri(f"http://{EC2_PUBLIC_DNS}:5000")
    mlflow.set_experiment("xgboost_optimized_model")

@task
def load_and_prepare_data(data_path):
    cleaned_df = pd.read_csv(data_path)
    X = cleaned_df.drop(columns=['price'])
    y = cleaned_df['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

@task
def get_optimized_params():
    params = {
        'learning_rate': 0.09455111298980684,
        'max_depth': 9,
        'min_child_weight': 0.3730492049381335,
        'n_estimators': 500,
        'subsample': 0.9989341273723211,
        'objective': 'reg:squarederror',
        'eval_metric': 'rmse'
    }
    return params

@task(log_prints=True)
def train_and_log_model(X_train, X_test, y_train, y_test, params):
    with mlflow.start_run():
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mlflow.log_params(params)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2_score", r2)
        signature = mlflow.models.signature.infer_signature(X_train, y_train)
        input_example = X_train[:1]
        mlflow.xgboost.log_model(model, artifact_path="xgboost_model", signature=signature, input_example=input_example)
        print(f"RMSE: {rmse}, MAE: {mae}, R2 Score: {r2}")

@flow
def model_training_flow(cleaned_data_path):
    setup_mlflow()
    X_train, X_test, y_train, y_test = load_and_prepare_data(cleaned_data_path)
    params = get_optimized_params()
    train_and_log_model(X_train, X_test, y_train, y_test, params)


# --- Main Flow ---

@flow
def main_flow(data_dir, combined_output_file, cleaned_output_file):
    # Run data preprocessing flow
    data_preprocessing_flow(data_dir, combined_output_file, cleaned_output_file)

    # Run model training flow
    model_training_flow(cleaned_output_file)

# Execute the main flow
if __name__ == "__main__":
    data_dir = '../data/original/'
    combined_output_file = '../data/combined_car_data.csv'
    cleaned_output_file = '../data/cleaned_car_data.csv'
    main_flow(data_dir, combined_output_file, cleaned_output_file)
