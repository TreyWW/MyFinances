import threading
from backend.finance.models import InvoiceRecurringProfile
from backend.core.service.boto3.scheduler.update_schedule import update_boto_schedule


# thread = threading.Thread(target=self._send_message, args=(func_name, args, kwargs))
# threads = list()
# thread.start()

# def fetch_and_update_profile(profile: InvoiceRecurringProfile):
#     update_boto_schedule(profile.id)


def refresh_all_schedules_statuses():
    print("REFRESHING ALL SCHEDULE STATUSES!!!!!!!!!!!!!!!!!!")
    threads: list = []

    all_recurring_profiles = InvoiceRecurringProfile.objects.filter(active=True).all()

    for profile in all_recurring_profiles:
        x = threading.Thread(target=update_boto_schedule, args=(profile.id,))
        threads.append(x)
        x.start()
