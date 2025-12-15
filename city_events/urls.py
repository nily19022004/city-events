from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from events import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)