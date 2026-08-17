from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from config.views import (
    login_view,
    logout_view,
    dashboard,
    posts_view,
    post_create_view,
    post_edit_view,
    post_delete_view,
    schedule_view,
    schedule_create_view,
    schedule_delete_view,
    generate_view,
    settings_view,
    test_ig_connection_view,
    approval_view,
    approve_post_view,
    reject_post_view,
    monitoring_view,
    health_check_view,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("posts/", posts_view, name="posts"),
    path("posts/create/", post_create_view, name="post_create"),
    path("posts/edit/<int:pk>/", post_edit_view, name="post_edit"),
    path("posts/delete/<int:pk>/", post_delete_view, name="post_delete"),
    path("schedule/", schedule_view, name="schedule"),
    path("schedule/create/", schedule_create_view, name="schedule_create"),
    path("schedule/delete/<int:pk>/", schedule_delete_view, name="schedule_delete"),
    path("generate/", generate_view, name="generate"),
    path("settings/", settings_view, name="settings"),
    path("settings/test-ig/", test_ig_connection_view, name="test_ig_connection"),
    path("approval/", approval_view, name="approval"),
    path("approval/approve/<int:pk>/", approve_post_view, name="approve_post"),
    path("approval/reject/<int:pk>/", reject_post_view, name="reject_post"),
    path("monitoring/", monitoring_view, name="monitoring"),
    path("health/", health_check_view, name="health_check"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
