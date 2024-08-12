conda env create -f xgboost_model/conda.yaml
conda activate mlflow-env

python3 app.py

python3 test_predict.py

Prediction: [12456.75]  # Example output
