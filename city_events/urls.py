from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from events import views

urlpatterns = [
    # Django admin (встроенная панель)
    path('django-admin/', admin.site.urls),
    
    # Публичные страницы
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Административная панель (кастомная)
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/events/', views.admin_events, name='admin_events'),
    path('admin/events/add/', views.admin_event_add, name='admin_event_add'),
    path('admin/events/<int:event_id>/edit/', views.admin_event_edit, name='admin_event_edit'),
    path('admin/events/<int:event_id>/toggle/', views.admin_event_toggle, name='admin_event_toggle'),
    path('admin/events/<int:event_id>/delete/', views.admin_event_delete, name='admin_event_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)