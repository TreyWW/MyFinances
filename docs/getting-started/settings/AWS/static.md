# Static Files

Coming Soon

[//]: # ()

[//]: # (## Using AWS with MyFinances)

[//]: # ()

[//]: # (You can use a few of the AWS Services with our project. Some key use cases are [S3]&#40;&#41; and [CloudFront CDN]&#40;&#41;)

[//]: # ()

[//]: # ()

[//]: # (> More information on how to set this up will come soon. This is just a prototype while we test our staging environment)

[//]: # ()

[//]: # (### Setting up Static CDN with AWS)

[//]: # ()

[//]: # (#### Variables)

[//]: # ()

[//]: # (AWS_STATIC_ENABLED: &#40;True/False&#41; whether static files should be served through AWS)

[//]: # (Alternative to AWS_STATIC_ENABLED is setting "STATIC_CDN_TYPE" equal to "AWS")

[//]: # ()

[//]: # (AWS_STATIC_LOCATION: The bucket path for static files. E.g. "bucket.com/`static`/main.js". So in this case `static` would be the)

[//]: # (location.)

[//]: # ()

[//]: # (AWS_STATIC_BUCKET_NAME: [REQUIRED] The bucket name for static files. E.g. "https://`myfinances`.s3.eu-west-2.amazonaws.com")

[//]: # (`myfinances`)

[//]: # (would be the bucket name)

[//]: # ()

[//]: # (AWS_STATIC_CUSTOM_DOMAIN: This would be the Cloudfront CDN url. For example `https://dxguxx2xxxx7x.cloudfront.net`. This can)

[//]: # (also be an "Alternate domain name" that's set on Cloudfront.)

[//]: # ()

[//]: # (AWS_STATIC_REGION_NAME: The region which your S3 bucket is hosted in. E.g. `eu-west-2` is london.)

[//]: # ()

[//]: # (### Setting up Public Media with AWS)

[//]: # ()

[//]: # (Public Media is media that users upload such as profile pictures)

[//]: # ()

[//]: # (#### Variables)

[//]: # ()

[//]: # (AWS_MEDIA_PUBLIC_ENABLED: &#40;True/False&#41; whether static files should be served through AWS)

[//]: # ()

[//]: # (AWS_MEDIA_PUBLIC_LOCATION: The bucket path for public media files. E.g. "bucket.)

[//]: # (com/`myfinances/media/public`/profile_pic.png".)

[//]: # (So in this case `myfinances/media/public`would be the location.)

[//]: # ()

[//]: # (AWS_MEDIA_PUBLIC_BUCKET_NAME: [REQUIRED] The bucket name for public media files. E.g. "https://`myfinances`)

[//]: # (.s3.eu-west-2.amazonaws.com")

[//]: # (`myfinances` would be the bucket name)

[//]: # ()

[//]: # (AWS_MEDIA_PUBLIC_FILE_OVERWRITE: &#40;True/False&#41; Whether files should be allowed to be overridden. It's recommended to have this)

[//]: # (turned off.)

[//]: # ()

[//]: # (AWS_MEDIA_PUBLIC_CUSTOM_DOMAIN: This would be the Cloudfront CDN url. For example `https://dxguxx2xxxx7x.cloudfront.net`. This can)

[//]: # (also be an "Alternate domain name" that's set on Cloudfront.)

[//]: # ()

[//]: # (AWS_MEDIA_PUBLIC_ACCESS_KEY_ID: An IAM user security access key ID)

[//]: # (AWS_MEDIA_PUBLIC_ACCESS_KEY: An IAM user security access key secret)

[//]: # ()

[//]: # (### Setting up Private Media with AWS)

[//]: # ()

[//]: # (Private Media is media that users upload such as receipt images.)

[//]: # ()

[//]: # (#### Variables)

[//]: # ()

[//]: # (AWS_MEDIA_PRIVATE_ENABLED: &#40;True/False&#41; whether static files should be served through AWS)

[//]: # ()

[//]: # (AWS_MEDIA_PRIVATE_LOCATION: The bucket path for private media files. E.g. "bucket.)

[//]: # (com/`myfinances/media/private`/profile_pic.png".)

[//]: # (So in this case `myfinances/media/private`would be the location.)

[//]: # ()

[//]: # (AWS_MEDIA_PRIVATE_BUCKET_NAME: [REQUIRED] The bucket name for private media files. E.g. "https://`myfinances`)

[//]: # (.s3.eu-west-2.amazonaws.com")

[//]: # (`myfinances` would be the bucket name)

[//]: # ()

[//]: # (AWS_MEDIA_PRIVATE_FILE_OVERWRITE: &#40;True/False&#41; Whether files should be allowed to be overridden. It's recommended to have this)

[//]: # (turned off.)

[//]: # ()

[//]: # (AWS_MEDIA_PRIVATE_REGION_NAME: The region which your S3 bucket is hosted in. E.g. `eu-west-2` is london.)

[//]: # ()

[//]: # (AWS_MEDIA_PRIVATE_CUSTOM_DOMAIN: This would be the Cloudfront CDN url. For example `https://dxguxx2xxxx7x.cloudfront.net`. This)

[//]: # (can)

[//]: # (also be an "Alternate domain name" that's set on Cloudfront.)

[//]: # ()

[//]: # (AWS_MEDIA_PRIVATE_ACCESS_KEY_ID: An IAM user security access key ID)

[//]: # (AWS_MEDIA_PRIVATE_ACCESS_KEY: An IAM user security access key secret)

[//]: # (AWS_MEDIA_PRIVATE_CLOUDFRONT_PUBLIC_KEY_ID: A public key ID for cloudfront [view here]&#40;https://us-east-1.console.aws.amazon.)

[//]: # (com/cloudfront/v4/home/publickey&#41;)

[//]: # (AWS_MEDIA_PRIVATE_CLOUDFRONT_PRIVATE_KEY: A BASE 64 ENCODED private key string that matches)

[//]: # (AWS_MEDIA_PRIVATE_CLOUDFRONT_PUBLIC_KEY_ID. May)

[//]: # (start with something like `-----BEGIN RSA PRIVATE KEY-----` or `-----BEGIN PRIVATE KEY-----`.)

[//]: # ()

[//]: # (The easiest way to do this is to open a python terminal `$ py` and type:)

[//]: # ()

[//]: # (```python)

[//]: # (import base64)

[//]: # ()

[//]: # (temp = base64.b64encode&#40;b"""-----BEGIN RSA PRIVATE KEY-----KEY-----END RSA PRIVATE KEY-----"""&#41;)

[//]: # (print&#40;temp&#41;)

[//]: # (```)

[//]: # ()

[//]: # (!> If you get an `Could not deserialize key data` ValueError, this is because the PRIVATE_KEY is formatted incorrectly. Python)

[//]: # (needs the key WITH new lines! This is the most annoying bug to debug.)
