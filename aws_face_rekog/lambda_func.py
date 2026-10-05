import json
import base64
import boto3

rekognition = boto3.client("rekognition")


def lambda_handler(event, context):

    # -----------------------------------
    # WEB REQUEST
    # -----------------------------------

    if "body" in event:

        body = event["body"]

        # API Gateway may base64-encode the entire HTTP body
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")

        data = json.loads(body)

        # Get image sent by the webpage
        image_base64 = data["image"]

        # Convert Base64 → actual image bytes
        image_bytes = base64.b64decode(image_base64)

        # Send image directly to Rekognition
        response = rekognition.detect_faces(
            Image={
                "Bytes": image_bytes
            },
            Attributes=["DEFAULT"]
        )

        face_count = len(response["FaceDetails"])

        print(f"Number of faces detected: {face_count}")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "face_count": face_count
            })
        }


    # -----------------------------------
    # S3 EVENT
    # -----------------------------------

    else:

        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        object_key = event["Records"][0]["s3"]["object"]["key"]

        print(f"Bucket: {bucket_name}")
        print(f"Image: {object_key}")

        response = rekognition.detect_faces(
            Image={
                "S3Object": {
                    "Bucket": bucket_name,
                    "Name": object_key
                }
            },
            Attributes=["DEFAULT"]
        )

        face_count = len(response["FaceDetails"])

        print(f"Number of faces detected: {face_count}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "face_count": face_count
            })
        }
