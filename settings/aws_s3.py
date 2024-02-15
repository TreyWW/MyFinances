from django.utils.deconstruct import deconstructible
from storages.backends.s3boto3 import S3Boto3Storage

from settings.settings import STATICFILES_LOCATION, AWS_CDN_S3_CUSTOM_DOMAIN, AWS_STORAGE_BUCKET_NAME


@deconstructible
class StaticStorage(S3Boto3Storage):
    location = STATICFILES_LOCATION

    def __init__(self, *args, **kwargs):
        kwargs["custom_domain"] = AWS_CDN_S3_CUSTOM_DOMAIN

        super(StaticStorage, self).__init__(*args, **kwargs)


@deconstructible
class MediaStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        kwargs["bucket"] = AWS_STORAGE_BUCKET_NAME

        super(MediaStorage, self).__init__(*args, **kwargs)
