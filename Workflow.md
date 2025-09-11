🔹 Prerequisites

Kali Linux with Localstack running on port 4566.

AWS CLI installed and configured.

Python 3 with boto3 installed in a virtual environment.

🔹 Steps
1. Create S3 Buckets
aws --endpoint-url=http://localhost:4566 s3 mb s3://yash-test-bucket-checkov
aws --endpoint-url=http://localhost:4566 s3 mb s3://yash-test-bucket-logs
aws --endpoint-url=http://localhost:4566 s3 mb s3://yash-test-bucket-replica-checkov


Verify:

aws --endpoint-url=http://localhost:4566 s3 ls

2. Create SNS Topic
aws --endpoint-url=http://localhost:4566 sns create-topic --name s3-event-topic


Expected output:

{
  "TopicArn": "arn:aws:sns:us-east-1:000000000000:s3-event-topic"
}

3. Create SQS Queue
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name mysqs


Expected output:

{
  "QueueUrl": "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/mysqs"
}

4. Subscribe SQS to SNS
aws --endpoint-url=http://localhost:4566 sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:000000000000:s3-event-topic \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:000000000000:mysqs


Expected output:

{
  "SubscriptionArn": "arn:aws:sns:us-east-1:000000000000:s3-event-topic:xxxx-xxxx-xxxx"
}

5. Configure S3 Event Notification

Create a JSON file (s3_event_config.json):

{
  "TopicConfigurations": [
    {
      "Id": "s3-event-config",
      "TopicArn": "arn:aws:sns:us-east-1:000000000000:s3-event-topic",
      "Events": ["s3:ObjectCreated:*"]
    }
  ]
}


Apply it to your S3 bucket:

aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration \
  --bucket yash-test-bucket-checkov \
  --notification-configuration file://s3_event_config.json

6. Upload File to Trigger Event
echo "SNS event test" > test.txt
aws --endpoint-url=http://localhost:4566 s3 cp test.txt s3://yash-test-bucket-checkov/

7. Check Messages in SQS
aws --endpoint-url=http://localhost:4566 sqs receive-message \
  --queue-url http://localhost:4566/000000000000/mysqs


You should see a JSON payload with S3 event details.

8. Consume Events with Python

Activate your virtual environment and install boto3:

python3 -m venv venv
source venv/bin/activate
pip install boto3


Python script (test_s3_event.py):

import boto3
import json

s3 = boto3.client("s3", endpoint_url="http://localhost:4566")
sqs = boto3.client("sqs", endpoint_url="http://localhost:4566")

queue_url = "http://localhost:4566/000000000000/mysqs"

# Upload test file
with open("test2.txt", "w") as f:
    f.write("SNS event test via Python")

s3.upload_file("test2.txt", "yash-test-bucket-checkov", "test2.txt")
print("✅ Uploaded file to S3")

# Poll SQS
resp = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=2)

if "Messages" in resp:
    body = json.loads(resp["Messages"][0]["Body"])
    print("✅ Got S3 event:")
    print(json.dumps(json.loads(body["Message"]), indent=2))
else:
    print("⚠️ No messages received.")


Run:

python3 test_s3_event.py

