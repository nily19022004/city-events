from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Event

def event_list(request):
    """Главная страница - список будущих мероприятий"""
    events = Event.objects.filter(
        is_active=True,
        date__gte=timezone.now().date()
    ).order_by('date', 'time')
    
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    """Страница деталей мероприятия"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    return render(request, 'events/event_detail.html', {'event': event})