import logging
from backend.core.api.public import APIAuthToken
from rest_framework.decorators import api_view

from backend.core.service.asyn_tasks.tasks import Task
from backend.core.api.public.helpers.response import APIResponse


@api_view(["POST"])
def webhook_task_queue_handler_view_endpoint(request):
    token: APIAuthToken | None = request.auth

    if not token:
        return APIResponse(False, {"status": "error", "message": "No token found"}, status=500)

    if not token.administrator_service_type == token.AdministratorServiceTypes.AWS_WEBHOOK_CALLBACK:
        return APIResponse(False, {"status": "error", "message": "Invalid API key for this service"}, status=500)

    try:
        data: dict = request.data
        func_name: str = data.get("func_name")
        args: list = data.get("args", [])
        kwargs: dict = data.get("kwargs", {})

        print(f"Function Name: {func_name}")
        print(f"Arguments: {args}")
        print(f"Keyword Arguments: {kwargs}")

        # Validate function name
        if not func_name:
            raise ValueError("Function name is required.")

        # Create an instance of Task
        task_helper = Task()

        # Attempt to execute the function
        result = task_helper.execute_now(func_name, *args, **kwargs)

        # Handle the result (e.g., store it or log it)
        print(f"Webhook executed: {func_name} with result: {result}")

        return APIResponse(True, {"status": "success", "result": result})

    except Exception as e:
        logging.error(f"Error executing webhook task: {str(e)}")
        return APIResponse(False, {"status": "error", "message": "An internal error has occurred."}, status=500)
