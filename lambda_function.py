import json
import boto3
import urllib

def lambda_handler(event, context):

    # The function is called every time a file is added to the S3 Bucket
    # Fetch Bucket Name, File name from the event
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    key=event["Records"][0]['s3']['object']['key']
    key = urllib.parse.unquote_plus(key,encoding="utf-8")

    # Create an S3 Client
    s3_client = boto3.client("s3")

    # Fetch this particular file and its contents
    s3_response = s3_client.get_object(Bucket=bucket_name, Key=key)
    file_contents = s3_response["Body"].read().decode()
    file_contents = json.loads(file_contents)

    # Get the Details viz. email and name
    name = file_contents['name']
    email = file_contents['email']

    # Create an SES Client
    ses_client = boto3.client("ses")

    # Create an Email Template (also can be done in SES Dashboard)

    subject = "Thank you for applying!"

    body = f"""
        <br />
        <p>
        Hello {name}, <br />
        We at One Byte Inc. really like your profile and would like to 
take your application to the next stage.
        <br />
        We would like to take a telephone interview in the coming week. 
Please click on this <a href="shorturl.at/ehjy9">link</a> to acknowledge 
the invite and schedule the meeting based on your convenience. 
        <br/>


        <br />
        <br />
        Best Regards, <br />
        Sreekesh Iyer <br />
        <small>Recruitment Manager<br />
        One Byte Inc.</small>
        </p>
    """

    message = {
        "Subject": {
            "Data": subject
        },
        "Body": {
            "Html": {
                "Data": body
            }
        }
    }

    # Send the email
    ses_response = ses_client.send_email(Source="sourceemail@gmail.com", Destination={
        "ToAddresses": [
            email
            ]
    },
    Message=message
    )
