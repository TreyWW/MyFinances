from django.http import JsonResponse
from django.views.decorators.http import require_GET
from backend.models import DefaultValues

@require_GET
def get_bank_details(request):
    try:
        default_values = DefaultValues.objects.get(user=request.user)
        bank_details = default_values.bank_details.all()

        bank_details_list = [
            {
                'id': bank_detail.id,
                'account_holder_name': bank_detail.account_holder_name,
                'account_number': bank_detail.account_number,
                'sort_code': bank_detail.sort_code,
            }
            for bank_detail in bank_details
        ]

        return JsonResponse({'status': 'success', 'bank_details': bank_details_list})
    except DefaultValues.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No saved bank details found'}, status=404)
