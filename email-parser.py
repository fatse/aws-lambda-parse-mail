import json
import boto3
import email
import os
import uuid

bucket = os.environ['inbound_mail_bucket']
outputBucket = os.environ['parsed_attachment_bucket']
s3 = boto3.client('s3')
s3resource = boto3.resource('s3')

def lambda_handler(event, context):
    key = event["Records"][0]["ses"]["mail"]["messageId"]
    waiterFlg = s3.get_waiter('object_exists')
    waiterFlg.wait(Bucket=bucket, Key=key)
    
    response = s3resource.Bucket(bucket).Object(key)

    messageBody = response.get()["Body"].read().decode('utf-8') 
    message = email.message_from_string(str(messageBody))
    
    if len(message.get_payload()) == 2:
        attachment = message.get_payload()[1]
        tmp_file_directory = '/tmp/'+attachment.get_filename()+str(uuid.uuid4())
        print(attachment.get_filename())
        print(attachment.get_content_type())
        
        attachment_content = attachment.get_payload(decode=True)
        print(attachment_content)

        if os.path.exists(tmp_file_directory):
            os.remove(tmp_file_directory)
        with open(tmp_file_directory, 'wb') as tmp_file:
            tmp_file.write(attachment_content)

        s3resource.meta.client.upload_file(tmp_file_directory, outputBucket, attachment.get_filename())
        os.remove(tmp_file_directory)
        
    else:
        print("Could not see file/attachment.")
    # TODO implement
    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }

