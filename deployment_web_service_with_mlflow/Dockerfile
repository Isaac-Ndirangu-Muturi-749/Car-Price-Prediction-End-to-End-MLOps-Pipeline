# Use a base image with Python and Conda installed
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy your project files
COPY . .

# Install the required packages from the conda environment
RUN conda env create -n car_price_prediction_env -f xgboost_model/conda.yaml

# Activate the conda environment
SHELL ["conda", "run", "-n", "car_price_prediction_env", "/bin/bash", "-c"]

# Run the model application
CMD ["conda", "run", "-n", "car_price_prediction_env", "python", "app.py"]
