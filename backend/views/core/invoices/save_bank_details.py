from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from backend.models import BankDetail, DefaultValues

@csrf_exempt
@require_POST
def save_bank_details(request):
    try:
        # Extract the form data from the POST request
        account_holder_name = request.POST.get('account_holder_name')
        account_number = request.POST.get('account_number')
        sort_code = request.POST.get('sort_code')

        # Check if all required fields are filled
        if not (account_holder_name and account_number and sort_code):
            return JsonResponse({'status': 'error', 'message': 'Invalid data'})

        # Create the BankDetail object and add it to DefaultValues
        bank_detail = BankDetail.objects.create(
            account_holder_name=account_holder_name,
            account_number=account_number,
            sort_code=sort_code
        )

        # Get or create DefaultValues for the user
        default_values, _ = DefaultValues.objects.get_or_create(user=request.user)
        default_values.bank_details.add(bank_detail)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(f"Error saving bank details: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})