#!/usr/bin/env bash

echo "Building Docker image..."
docker build -t car-price-prediction-integration-test .

echo "Running the Docker container..."
docker run -d -p 5000:5000 --name car_price_predictor car-price-prediction-integration-test

echo "Waiting for the app to start..."
sleep 10

echo "Running the integration test..."
python3 test_integration.py

echo "Cleaning up..."
docker stop car_price_predictor
docker rm car_price_predictor

echo "Integration test completed!"
