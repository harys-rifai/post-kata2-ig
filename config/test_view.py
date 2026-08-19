from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.utils import timezone
from datetime import timedelta

@login_required
def test_category_view(request):
    week_ago = timezone.now() - timedelta(days=7)
    qs = Post.objects.filter(status="published", updated_at__gte=week_ago).order_by("-updated_at")[:5]
    data = list(qs.values("id", "title", "category"))
    return JsonResponse({"posts": data, "count": len(data)})
