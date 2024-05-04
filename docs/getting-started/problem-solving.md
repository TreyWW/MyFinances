Here are some set-up hiccups that have occured for some and the solutions that we have come up with so far:

1. ImportError: cannot import name 'login_not_required' from 'login_required

To fix this:
```shell
pip install django-login-required-middleware
```

2. No module named 'forex_python'

To fix this:
```shell
pip install forex_python
```

3. Several boto3 extensions not found errors 

To fix these:
```shell
pip install mypy_boto3_iam

pip install mypy_boto3_scheduler

pip install mypy_boto3_events

pip install mypy_boto3_stepfunctions
```
