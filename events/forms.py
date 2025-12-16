from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Event
import re


class EventForm(forms.ModelForm):
    """Форма для добавления и редактирования мероприятий"""
    
    class Meta:
        model = Event
        fields = ['title', 'date', 'time', 'location', 'description', 'image_url', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Название мероприятия'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
                'placeholder': 'дд.мм.гггг'
            }, format='%Y-%m-%d'),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'placeholder': '--:--'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'например, Центральный парк'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'required': True,
                'placeholder': 'Полное описание мероприятия'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_date(self):
        """Проверка, что дата не в прошлом"""
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError('Нельзя создать мероприятие с прошедшей датой.')
        return date
    
    def clean_image_url(self):
        """Проверка URL изображения (если указан)"""
        image_url = self.cleaned_data.get('image_url')
        if image_url:
            # Простая проверка формата URL
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(image_url):
                raise ValidationError('Введите корректный URL изображения.')
        return image_url
    
    def clean_description(self):
        """Экранирование HTML-тегов для защиты от XSS"""
        description = self.cleaned_data.get('description')
        if description:
            # Django автоматически экранирует HTML при рендеринге в шаблонах через |escape
            # Дополнительная проверка на потенциально опасные теги
            # Простая защита: удаляем явные скрипты
            dangerous_patterns = ['<script', '</script>', 'javascript:', 'onerror=', 'onclick=']
            description_lower = description.lower()
            for pattern in dangerous_patterns:
                if pattern in description_lower:
                    raise ValidationError('Описание содержит недопустимые элементы.')
        return description
    
    def clean_is_active(self):
        """Проверка, что нельзя активировать прошедшее событие"""
        is_active = self.cleaned_data.get('is_active')
        date = self.cleaned_data.get('date')
        time = self.cleaned_data.get('time')
        
        # Если пытаемся активировать событие
        if is_active:
            now = timezone.now()
            now_date = now.date()
            now_time = now.time()
            
            # Проверяем, прошло ли событие
            if date and date < now_date:
                raise ValidationError('Нельзя активировать событие с прошедшей датой.')
            
            if date and date == now_date and time and time <= now_time:
                raise ValidationError('Нельзя активировать событие, которое уже прошло.')
        
        return is_active

