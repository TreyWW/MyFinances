import os
import json
import uuid
import threading
import boto3
import inspect

from django.urls import reverse


class Task:
    def __init__(self, queue_url=None):
        self.queue_url: str | None = queue_url or os.environ.get("AWS_SQS_QUEUE_URL")
        self.region_name = os.environ.get("AWS_REGION_NAME")
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_ACCESS_KEY")
        self.WEBHOOK_URL = os.environ.get("SITE_URL", default="http://127.0.0.1:8000") + reverse("api:public:webhooks:receive_global")

        if self.queue_url:
            self.sqs_client = boto3.client(
                "sqs",
                # aws_access_key_id=self.aws_access_key_id,
                # aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )
        else:
            self.sqs_client = None  # Only set up SQS client if queue_url is provided

    def queue_task(self, func, *args, **kwargs):
        # Determine if func is a string or callable
        if isinstance(func, str):
            func_name = func
        elif callable(func):
            func_name = self._get_function_path(func)
        else:
            raise ValueError("func must be a callable or a string representing the function name.")

        # If SQS is not configured, execute the function directly
        if not self.queue_url or not self.region_name:
            return self.execute_now(func_name, *args, **kwargs)

        print("TASK 3 - call _send_message to SQS")
        # Use threading to send the message to SQS
        thread = threading.Thread(target=self._send_message, args=(func_name, args, kwargs))
        thread.start()

        return "Task submitted to SQS"

    def _send_message(self, func_name, args, kwargs):
        message_body = {"func_name": func_name, "args": args, "kwargs": kwargs, "webhook_url": self.WEBHOOK_URL}
        print(message_body)

        try:
            print("TASK 4 - Send SQS message")
            res = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageGroupId="default",
                MessageDeduplicationId=str(uuid.uuid4()),
            )
            print(f"SQS Response: {res}")
        except Exception as e:
            print(f"Error sending message to SQS: {str(e)}")
            return self.execute_now(func_name, *args, **kwargs)

    def execute_now(self, func_name, *args, **kwargs):
        print("TASK 6 - Execute function directly")
        if "." not in func_name:
            raise ValueError(f"Invalid function name: {func_name}. Must include module path.")

        func = globals().get(func_name)
        if func is None:
            try:
                module_name, func_name = func_name.rsplit(".", 1)
                module = __import__(module_name, fromlist=[func_name])
                func = getattr(module, func_name)
            except (ImportError, AttributeError) as e:
                raise ValueError(f"Function {func_name} not found: {str(e)}")

        if callable(func):
            return func(*args, **kwargs)
        else:
            raise ValueError(f"Function {func_name} is not callable")

    def _get_function_path(self, func):
        """Returns the full path of the function as a string."""
        module = inspect.getmodule(func).__name__
        func_name = func.__name__  # Use __name__ instead of __qualname__
        return f"{module}.{func_name}"


# Usage Example
# task_instance = Task()
# result = task_instance.queue_task('my_module.my_function', arg1, arg2)  # Using string
# result = task_instance.queue_task(my_function, arg1, arg2)  # Using callable
