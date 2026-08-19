from posts.models import Post, Notification

def notification_count(request):
    """Provide notification count for the navbar badge."""
    if not request.user.is_authenticated:
        return {"notification_count": 0}
    try:
        return {"notification_count": Notification.objects.filter(user=request.user, is_read=False).count()}
    except Exception:
        return {"notification_count": 0}
