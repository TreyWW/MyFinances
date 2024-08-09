from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST

from backend.service.asyn_tasks.tasks import Task


@csrf_exempt
@require_POST
def webhook_task_queue_handler_view_endpoint(request):
    print("TASK 5 - Webhook Callback")
    try:
        data: dict = json.loads(request.body)
        func_name: str = data.get("func_name")
        args: list = data.get("args", [])
        kwargs: dict = data.get("kwargs", {})

        print(data)
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

        return JsonResponse({"status": "success", "result": result})

    except Exception as e:
        print(f"Error executing webhook task: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
