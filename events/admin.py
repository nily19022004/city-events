from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'is_active')
    list_filter = ('is_active', 'date')
    search_fields = ('title', 'location')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'date', 'time', 'location', 'description')
        }),
        ('Изображение', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        }),
        ('Системные настройки', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )