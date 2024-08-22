## **Common error messages and their solutions:**

1. If you receive this error: **ImportError: cannot import name 'login_not_required' from 'login_required** <br /> You may be missing some django middleware.

To fix this:
```shell
pip install django-login-required-middleware
```

2. To fix several **boto3** "extension name here" **not found errors** 

Do the following:
```shell
pip install mypy_boto3_iam

pip install mypy_boto3_scheduler

pip install mypy_boto3_events

pip install mypy_boto3_stepfunctions
```