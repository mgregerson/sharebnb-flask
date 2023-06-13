import logging
import boto3
from botocore.exceptions import ClientError
import os
import mimetypes


s3 = boto3.client(
  "s3",
  "us-east-1",
  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

bucket = os.getenv('BUCKET_NAME')


def upload_file(file_name,
                bucket=bucket,
                object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: Response if file was uploaded, else False
    """
    
    mimetype, encoding = mimetypes.guess_type(file_name)
    print(bucket);

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = s3

    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ContentDisposition': 'inline',
                                                                                    'ContentType': mimetype})
        return response
    except ClientError as e:
        logging.error(e)
        return False

def download(file_name, bucket=bucket, object_name=None ):
    """Downloads file from AWS S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: Output of downloaded file
    """

    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = s3

    output = s3_client.download_file(bucket, object_name, file_name)

    
    return output

def list_all_files(bucket):
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)
    return contents