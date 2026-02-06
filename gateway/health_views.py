# gateway/health_views.py
from django.http import HttpResponse
from django.views.decorators.http import require_GET

@require_GET
def health_check(request):
    """Simple health check endpoint for Render/Railway"""
    return HttpResponse("OK", status=200, content_type="text/plain")