# Variables
LOCAL_TAG := $(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME := car-price-prediction-integration-test:$(LOCAL_TAG)

# Target to run unit tests
test:
	pytest unit_tests/

# Target for quality checks
quality_checks:
	isort .
	black .
	pylint --recursive=y .

# Build Docker image and run integration tests
build: quality_checks test
	docker build -t $(LOCAL_IMAGE_NAME) -f integration-test/Dockerfile .

# Run integration tests using Docker container
integration_test: build
	# Ensure any existing container is stopped and removed
	docker rm -f car_price_predictor || true
	# Run the Docker container
	docker run -d -p 5000:5000 --name car_price_predictor $(LOCAL_IMAGE_NAME)
	# Wait for the app to start
	sleep 10
	# Execute integration tests
	bash integration-test/run_integration_test.sh
	# Clean up
	docker stop car_price_predictor

# Setup environment
setup:
	pre-commit install

.PHONY: test quality_checks build integration_test setup
