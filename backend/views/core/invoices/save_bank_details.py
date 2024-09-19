import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from backend.models import BankDetail, DefaultValues

@csrf_exempt
@require_POST
def save_bank_details(request):
    try:
        data = json.loads(request.body)
        account_holder_name = data.get('account_holder_name')
        account_number = data.get('account_number')
        sort_code = data.get('sort_code')

        if not (account_holder_name and account_number and sort_code):
            return JsonResponse({'status': 'error', 'message': 'Invalid data'})

        bank_detail = BankDetail.objects.create(
            account_holder_name=account_holder_name,
            account_number=account_number,
            sort_code=sort_code
        )

        default_values, _ = DefaultValues.objects.get_or_create(user=request.user)
        default_values.bank_details.add(bank_detail)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(f"Error saving bank details: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})