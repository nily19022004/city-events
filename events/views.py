from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, time as dt_time
from .models import Event
from .forms import EventForm


def event_list(request):
    """Главная страница - список будущих мероприятий"""
    now = timezone.now()
    now_date = now.date()
    now_time = now.time()
    
    # Автоматически деактивируем все прошедшие активные события
    # Получаем все активные события и проверяем каждое
    all_active = list(Event.objects.filter(is_active=True).values('id', 'date', 'time'))
    events_to_deactivate = []
    
    for event_data in all_active:
        event_date = event_data['date']
        event_time = event_data['time']
        
        # Если дата в прошлом - событие точно прошло
        if event_date < now_date:
            events_to_deactivate.append(event_data['id'])
        # Если дата сегодня и время указано и уже прошло
        elif event_date == now_date and event_time is not None:
            event_datetime = timezone.make_aware(
                datetime.combine(event_date, event_time)
            )
            if event_datetime <= now:
                events_to_deactivate.append(event_data['id'])
    
    # Массово деактивируем прошедшие события
    if events_to_deactivate:
        Event.objects.filter(id__in=events_to_deactivate).update(is_active=False)
    
    # Фильтруем только активные события, которые еще не прошли
    # Используем двойную фильтрацию: по is_active и по дате/времени
    events = Event.objects.filter(
        is_active=True
    ).exclude(
        # Исключаем события с прошедшей датой
        date__lt=now_date
    ).exclude(
        # Исключаем события сегодня с прошедшим временем
        date=now_date,
        time__isnull=False,
        time__lte=now_time
    ).order_by('date', 'time')
    
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, event_id):
    """Страница деталей мероприятия"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    return render(request, 'events/event_detail.html', {'event': event})


def admin_login(request):
    """Страница входа в административную панель"""
    if request.user.is_authenticated:
        return redirect('admin_events')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему.')
            return redirect('admin_events')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'events/admin_login.html')


@login_required
def admin_logout(request):
    """Выход из административной панели"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('event_list')


@login_required
def admin_events(request):
    """Страница управления мероприятиями"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('event_list')
    
    now = timezone.now()
    now_date = now.date()
    now_time = now.time()
    
    # Автоматически деактивируем все прошедшие активные события
    all_active = list(Event.objects.filter(is_active=True).values('id', 'date', 'time'))
    events_to_deactivate = []
    
    for event_data in all_active:
        event_date = event_data['date']
        event_time = event_data['time']
        
        # Если дата в прошлом - событие точно прошло
        if event_date < now_date:
            events_to_deactivate.append(event_data['id'])
        # Если дата сегодня и время указано и уже прошло
        elif event_date == now_date and event_time is not None:
            if event_time <= now_time:
                events_to_deactivate.append(event_data['id'])
    
    # Массово деактивируем прошедшие события
    if events_to_deactivate:
        Event.objects.filter(id__in=events_to_deactivate).update(is_active=False)
    
    events = Event.objects.all().order_by('-date', '-time')
    
    # Поиск по названию или месту
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | Q(location__icontains=search_query)
        )
    
    return render(request, 'events/admin_events.html', {
        'events': events,
        'search_query': search_query
    })


@login_required
def admin_event_add(request):
    """Добавление нового мероприятия"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('event_list')
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Мероприятие успешно добавлено.')
            return redirect('admin_events')
    else:
        form = EventForm()
    
    return render(request, 'events/admin_event_form.html', {
        'form': form,
        'title': 'Добавить мероприятие',
        'action': 'add',
        'is_past': False
    })


@login_required
def admin_event_edit(request, event_id):
    """Редактирование мероприятия"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('event_list')
    
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Мероприятие успешно обновлено.')
            return redirect('admin_events')
    else:
        form = EventForm(instance=event)
    
    # Проверяем, прошло ли событие (для отображения в шаблоне)
    is_past = event.is_past() if event else False
    
    return render(request, 'events/admin_event_form.html', {
        'form': form,
        'event': event,
        'title': 'Редактировать мероприятие',
        'action': 'edit',
        'is_past': is_past
    })


@login_required
def admin_event_toggle(request, event_id):
    """Переключение статуса активности мероприятия"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('event_list')
    
    event = get_object_or_404(Event, id=event_id)
    
    # Если пытаемся активировать прошедшее событие - запрещаем
    if not event.is_active and event.is_past():
        messages.error(request, f'Нельзя активировать прошедшее мероприятие "{event.title}".')
        return redirect('admin_events')
    
    event.is_active = not event.is_active
    event.save()
    
    status = 'активировано' if event.is_active else 'деактивировано'
    messages.success(request, f'Мероприятие "{event.title}" {status}.')
    return redirect('admin_events')


@login_required
def admin_event_delete(request, event_id):
    """Удаление мероприятия"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('event_list')
    
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Мероприятие "{event_title}" успешно удалено.')
        return redirect('admin_events')
    
    return render(request, 'events/admin_event_delete.html', {'event': event})