from django.db import models
from django.utils import timezone
from datetime import datetime
import os

class Event(models.Model):
    # 1. Название (обязательное)
    title = models.CharField(
        max_length=200,
        verbose_name='Название мероприятия'
    )
    
    # 2. Дата проведения (обязательное)
    date = models.DateField(
        verbose_name='Дата проведения'
    )
    
    # 3. Время начала (необязательное)
    time = models.TimeField(
        verbose_name='Время начала',
        blank=True,
        null=True
    )
    
    # 4. Место проведения (обязательное)
    location = models.CharField(
        max_length=200,
        verbose_name='Место проведения'
    )
    
    # 5. Полное описание
    description = models.TextField(
        verbose_name='Описание мероприятия'
    )
    
    # 6. Изображение (необязательное) - УПРОЩЕННАЯ ВЕРСИЯ БЕЗ IMAGEFIELD
    image_url = models.CharField(
        verbose_name='Ссылка на изображение',
        max_length=500,
        blank=True,
        null=True
    )
    
    # 7. Флаг «Активно»
    is_active = models.BooleanField(
        verbose_name='Активно',
        default=True
    )
    
    # Дополнительные поля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"{self.title} ({self.date})"
    
    @property
    def short_description(self):
        """Короткий анонс (первые 100 символов)"""
        if len(self.description) > 100:
            return self.description[:100] + '...'
        return self.description
    
    def is_past(self):
        """Проверка, прошло ли событие"""
        now = timezone.now()
        now_date = now.date()
        now_time = now.time()
        
        # Если дата в прошлом - событие прошло
        if self.date < now_date:
            return True
        
        # Если дата сегодня и время указано - проверяем время
        if self.date == now_date and self.time is not None:
            if self.time <= now_time:
                return True
        
        return False
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической деактивации прошедших событий"""
        # Если событие прошло - автоматически деактивируем
        if self.is_past():
            self.is_active = False
        super().save(*args, **kwargs)