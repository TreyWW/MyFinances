import boto3

from settings.settings import (
    AWS_TEXTRACT_REGION_NAME,
    AWS_TEXTRACT_ACCESS_KEY_ID,
    AWS_TEXTRACT_ENABLED,
    AWS_TEXTRACT_SECRET_ACCESS_KEY,
)

boto_session: boto3.Session = boto3.Session(
    aws_access_key_id=AWS_TEXTRACT_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_TEXTRACT_SECRET_ACCESS_KEY,
    region_name=AWS_TEXTRACT_REGION_NAME,
)

AWS_TEXTRACT_ENABLED = AWS_TEXTRACT_ENABLED
