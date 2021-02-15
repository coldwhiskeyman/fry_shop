from datetime import datetime, timedelta
from django.utils.timezone import utc

from shops.models import Purchase


class RemoveIncompletePurchasesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        purchases = Purchase.objects.filter(complete=False)
        now = datetime.utcnow().replace(tzinfo=utc)
        for purchase in purchases:
            if now - purchase.created > timedelta(hours=1):
                purchase.delete()
        return self.get_response(request)
