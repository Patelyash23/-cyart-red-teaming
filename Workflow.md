# Week 2 – S3 Event Notification with SNS + SQS (Localstack)

This workflow demonstrates setting up an event-driven architecture using **S3 + SNS + SQS** with Localstack. When a file is uploaded to S3, an event is published to SNS and delivered to an SQS queue, which is then consumed by a Python script.

---

## 🔹 Prerequisites
- Kali Linux with Localstack running on port `4566`
- AWS CLI installed and configured
- Python 3 with `boto3` installed in a virtual environment

---

## 🔹 Steps

### 1. Create S3 Buckets
```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://yash-test-bucket-checkov
aws --endpoint-url=http://localhost:4566 s3 mb s3://yash-test-bucket-logs
aws --endpoint-url=http://localhost:4566 s3 mb s3://yash-test-bucket-replica-checkov
