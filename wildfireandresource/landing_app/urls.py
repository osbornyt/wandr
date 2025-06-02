from django.urls import path, include
from landing_app import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'landing_app'

urlpatterns = [
    path("", views.show_landing, name="landing"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)