DB_ENDPOINT=mlflow-backend-db.czg4ecywqn0w.eu-north-1.rds.amazonaws.com
S3_BUCKET=mlflow-artifacts-capstone-mlops
PASSWORD=mlflowdb

mlflow server -h 0.0.0.0 -p 5000 \
    --backend-store-uri postgresql://mlflow:${PASSWORD}@${DB_ENDPOINT}:5432/mlflow_db \
    --default-artifact-root s3://${S3_BUCKET}


EC2_PUBLIC_DNS=ec2-16-16-217-131.eu-north-1.compute.amazonaws.com
http://ec2-16-16-217-131.eu-north-1.compute.amazonaws.com:5000