# Week 2 — Cloud Security Hands-on (LocalStack + Terraform)

## Prerequisites
- Docker
- Terraform
- AWS CLI (to interact with LocalStack)
- Python3 and virtualenv (for test script)

## Quick start
1. Start LocalStack
   sudo docker run -it -p 4566:4566 localstack/localstack

2. In a new terminal, export environment variables:
   export AWS_ACCESS_KEY_ID=test
   export AWS_SECRET_ACCESS_KEY=test
   export AWS_DEFAULT_REGION=us-east-1

3. Terraform:
   cd Week\ 2/terraform
   terraform init
   terraform validate
   terraform plan
   terraform apply -auto-approve

4. Create SQS & SNS (if Terraform did not create them):
   aws --endpoint-url=http://localhost:4566 sns create-topic --name s3-event-topic --region us-east-1
   aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name mysqs --region us-east-1
   aws --endpoint-url=http://localhost:4566 sns subscribe \
     --topic-arn arn:aws:sns:us-east-1:000000000000:s3-event-topic \
     --protocol sqs \
     --notification-endpoint arn:aws:sqs:us-east-1:000000000000:mysqs \
     --region us-east-1

5. Test upload:
   echo "SNS event test" > test.txt
   aws --endpoint-url=http://localhost:4566 s3 cp test.txt s3://yash-test-bucket-checkov/ --region us-east-1

6. Receive message on SQS:
   aws --endpoint-url=http://localhost:4566 sqs receive-message \
     --queue-url http://localhost:4566/000000000000/mysqs \
     --region us-east-1

7. Run Python test (in a venv):
   source venv/bin/activate
   pip install boto3
   python3 ../scripts/test_s3_event.py
