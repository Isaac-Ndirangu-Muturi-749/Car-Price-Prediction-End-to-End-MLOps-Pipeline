
# Car Price Prediction: End-to-End MLOps Pipeline

![MLOps Pipeline](images/mlops.png)

## Project Overview

This project implements an end-to-end MLOps pipeline for predicting car prices. It covers the entire workflow, from data preprocessing to model deployment and monitoring. The tools and technologies used ensure reproducibility, scalability, and efficient model management.

## Problem Statement

In today's dynamic automotive market, pricing used cars accurately is a complex challenge. Car prices vary significantly based on multiple factors such as brand, model, mileage, condition, and market demand. For both dealerships and individual sellers, incorrect pricing can result in lost revenue, longer sales cycles, or undervalued transactions. This project addresses these challenges by building an end-to-end machine learning pipeline for car price prediction. By leveraging data-driven insights and automating workflows, the pipeline ensures that predictions are accurate, scalable, and seamlessly integrated with deployment, monitoring, and continuous improvement processes.

## Project Structure

- **`data/`**: Raw and processed data files.
- **`data_preparation/`**: Scripts for data cleaning and preprocessing.
- **`deployment_web_service_with_mlflow/`**: Code for deploying the model using Flask and MLflow.
- **`infrastructure_as_code_with_cloud_formation/`**: AWS CloudFormation templates for infrastructure.
- **`integration-test/`**: Docker files and integration testing scripts.
- **`modelling/`**: Notebooks and scripts for model training and experiment tracking (MLflow).
- **`monitoring_with_evidently_and_grafana/`**: Scripts for monitoring using Evidently and Grafana.
- **`unit_tests/`**: Unit tests for various components.
- **`workflow_orchestration_with_prefect/`**: Prefect workflows for orchestration.

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Docker/Docker Compose**
- **AWS CLI**
- **Conda (for environment management)**
- **Pre-commit (for code formatting and linting)**

### Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Isaac-Ndirangu-Muturi-749/Car-Price-Prediction-End-to-End-MLOps-Pipeline.git
   cd Car-Price-Prediction-End-to-End-MLOps-Pipeline
   ```

2. **Install Dependencies**

   ```bash
   conda env create -n car_price_prediction_env -f conda.yaml
   conda activate car_price_prediction_env
   pre-commit install
   ```

3. **Setup Infrastructure**

CloudFormation is used to automate and manage AWS infrastructure for the Car Price Prediction project. With CloudFormation, you define resources such as EC2 instances, S3 buckets, RDS databases, and networking configurations in a JSON or YAML template. This allows you to create, update, and manage your infrastructure as code, ensuring consistency, repeatability, and scalability.

In this project, CloudFormation is used to deploy the following infrastructure:

- **RDS Database**: To store and retrieve car data for model training and predictions.
- **S3 Buckets**: For storing datasets and model artifacts.
- **EC2 Instances**: For running scripts, model training, and hosting the web service.

By using CloudFormation, the infrastructure setup process is streamlined, and the environment can be easily replicated across different stages (e.g., development, testing, production).

Deploy AWS infrastructure using CloudFormation:

   ```bash
   aws cloudformation create-stack --stack-name car-price-prediction-stack --template-body file://cloud_formation_template.yaml --parameters ParameterKey=DBUsername,ParameterValue=your-db-username ParameterKey=DBPassword,ParameterValue=your-db-password
   ```

4. **Build and Run Docker Containers**

   ```bash
   make integration_test
   ```

5. **Run Tests and Quality Checks**

   ```bash
   make test           # Run unit tests
   make quality_checks  # Run isort, black, pylint
   ```

6. **Deploy Model**

   ```bash
   make build
   ```

## Usage

### Data Preparation

Run the data cleaning and preprocessing script:

```bash
python data_preparation/data_preprocessing_and_cleaning.py
```

### Model Training

Model training scripts are located in the `modelling/` directory. The `xgboost_optimized_model.py` script performs hyperparameter tuning and trains the XGBoost model.

Example usage:

```bash
python modelling/experiment_tracking_with_mlflow/xgboost_optimized_model.py
```

### Experiment Tracking and Model Registry

Model experiments and training results are tracked using MLflow. Check the `modelling/experiment_tracking_with_mlflow/` directory for notebooks and scripts related to experiment tracking and the model registry.

### Workflow Orchestration with Prefect

#### Step 1: Install Dependencies

```bash
pip install -r workflow_orchestration_with_prefect/requirements.txt
```

#### Step 2: Start Prefect Server

```bash
prefect server start
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

#### Step 3: Run Workflow

```bash
python workflow_orchestration_with_prefect/workflow_orchestration.py
```

#### Step 4: Initialize and Deploy Prefect Flows

```bash
prefect project init
prefect deploy workflow_orchestration_with_prefect/workflow_orchestration.py:main_flow -n car-prediction-training -p zoompool
```

Start a worker and trigger flow execution:

```bash
prefect worker start --pool 'zoompool'
prefect deployment run 'main-flow/car-prediction-training'
```

#### Step 5: Schedule the Workflow

```bash
prefect deployment set-schedule main_flow/car-prediction-training --interval 120
```

### Model Deployment

1. **Build the Docker image:**

   ```bash
   docker build -t car-price-prediction-web-service deployment_web_service_with_mlflow/
   ```

2. **Run the container:**

   ```bash
   docker run -d -p 5000:5000 --name car_price_predictor car-price-prediction-web-service
   ```

### Monitoring

Start monitoring with Evidently and Grafana:

```bash
docker-compose -f monitoring_with_evidently_and_grafana/docker-compose.yml up
```

Access Grafana at `http://localhost:3000`.

![Monitoring Scheme](images/monitoring_scheme.png)

## Best Practices

- **Unit Tests**: Located in `unit_tests/`
- **Integration Tests**: Run via Docker
- **Code Quality**: Managed using isort, black, and pylint
- **Automation**: Controlled via Makefile and pre-commit hooks
- **CI/CD Pipeline**: Integrated through the Makefile and test scripts

### Unit Tests

- **Location**: `unit_tests/`

  Unit tests validate individual components of the project in isolation. These tests ensure that functions, classes, or methods behave as expected.

  - **Technologies Used**:
    - `unittest` or `pytest`
    - Mocking libraries like `unittest.mock`

  - **How to Run**:

    ```bash
    make test
    ```

### Integration Tests

- **Location**: `integration-test/`

  Integration tests verify that different components work together, such as testing the API endpoint and model service.

  - **How to Run**:

    ```bash
    make integration_test
    ```

### Code Quality

- **Tools**: `isort`, `black`, `pylint`

  Code quality tools enforce consistent formatting and catch errors early. Pre-commit hooks ensure these checks run before every commit.

  - **How to Run**:

    ```bash
    make quality_checks
    ```

### Automation

- **Makefile**: Automates tasks like testing, building, and deploying.

  Example commands:

  ```bash
  make build          # Build Docker image
  make test           # Run unit tests
  make quality_checks # Run code quality tools
  ```

- **Pre-commit Hooks**: Automatically run checks before every commit.

    Set up hooks:

    ```bash
    pre-commit install
    ```

### CI/CD Pipeline

- **CI/CD Integration**: Automates testing, building, and deployment using services like GitHub Actions.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Follow me on Twitter 🐦, connect with me on LinkedIn 🔗, and check out my GitHub 🐙. You won't be disappointed!

🐦 Twitter: https://x.com/NdiranguMuturi1

💼 LinkedIn: https://www.linkedin.com/in/isaac-muturi-3b6b2b237

🔗 GitHub: https://github.com/Isaac-Ndirangu-Muturi-749

---
