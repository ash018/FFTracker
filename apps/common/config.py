import boto3
from botocore.client import Config
from uuid import uuid4
from django.conf import settings

S3_KEY_ID = settings.S3_KEY_ID
S3_SECRET_KEY = settings.S3_SECRET_KEY
S3_BUCKET = settings.S3_BUCKET


def get_image_urls(request, obj_id, folder):
    s3 = boto3.resource(
        's3',
        'us-west-2',
        aws_access_key_id=S3_KEY_ID,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    url_list = []
    for value, image in request.FILES.items():
        image_name = folder + ('%s_%s_%s' % (uuid4(), obj_id, image.name))
        full_image_url = 'https://s3-us-west-2.amazonaws.com/' + S3_BUCKET + '/' + image_name
        s3.Bucket(S3_BUCKET).put_object(Key=image_name, Body=image)
        url_list.append(full_image_url)
    return url_list


def get_file_urls(request, user_id, folder):
    s3 = boto3.resource(
        's3',
        'us-west-2',
        aws_access_key_id=S3_KEY_ID,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    # TODO: Integrate s3 upload
    url_list = []
    for value, file in request.FILES.items():
        file_name = folder + ('%s_%s_%s' % (uuid4(), user_id, file.name))
        full_file_url = 'https://s3-us-west-2.amazonaws.com/' + S3_BUCKET + '/' + file_name
        s3.Bucket(S3_BUCKET).put_object(Key=file_name, Body=file)
        url_list.append(full_file_url)
    return url_list


def get_choices(dict_obj):
    return tuple((value, key) for key, value in dict_obj.items())
