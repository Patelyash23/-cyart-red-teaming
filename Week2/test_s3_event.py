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
