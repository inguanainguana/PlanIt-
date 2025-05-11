import random
from datetime import timedelta, datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F
from django.utils import timezone

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, NoReverseMatch
from django.template import Template, Context

from authapp.forms import AuthForm, RegForm, EditProfileForm
from authapp.models import image_format
from mainapp.models import Event, Task, Invitation, Expense, Income, Budget


def login(request):
    if request.method == 'POST':
        form = AuthForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            if user.is_superuser:
                return HttpResponseRedirect(reverse('admin:index'))
            return HttpResponseRedirect(reverse('mainapp:index'))
    else:
        form = AuthForm()

    context = {
        "title": "Войти",
        "description": "Войдите в свой аккаунт PlanIt!, чтобы получить доступ к инструментам для планирования мероприятий. Управляйте задачами, создавайте события и координируйте участников с легкостью.",
        "keywords": "авторизация, вход в аккаунт, PlanIt!, планирование мероприятий, управление задачами, координация участников, создание событий, веб-приложение, инструменты планирования, мероприятия",
        'form': form,
    }
    return render(request, 'authapp/login.html', context)


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('mainapp:index'))


def register(request):
    if request.method == 'POST':
        form = RegForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('authapp:login'))
    else:
        form = RegForm()
    context = {
        'title': 'Регистрация',
        "description": "Присоединяйтесь к PlanIt! и начните планировать свои мероприятия с легкостью. Создавайте события, управляйте задачами и координируйте участников всего в несколько кликов.",
        "keywords": "регистрация, PlanIt!, планирование мероприятий, организация мероприятий, управление задачами, координация участников, создание событий, инструменты для планирования, веб-приложение, мероприятия",
        'form': form,
    }
    return render(request, 'authapp/register.html', context)


phrases = [
    "Добро пожаловать в PlanIt! Готовы покорять новые вершины организации?",
    "Осторожно: чрезмерное планирование может привести к успешным мероприятиям!",
    "Привет, {{ user.username }}! Мы тут ждали, когда вы спасете мир... то есть, организуете следующее мероприятие.",
    "Привет, {{ user.username }}! Готовы помочь другим воплотить их мечты в реальность?",
    "Сплошные возможности: планируйте, мечтайте, действуйте!",
    "Добро пожаловать в PlanIt! Давайте вместе сделаем этот день максимально эффективным!",
    "Привет, {{ user.username }}! Ваши идеи расцветают здесь!"
]


@login_required
def profile_view(request):
    random_phrase = random.choice(phrases)
    template = Template(random_phrase)
    context = Context({'user': request.user})
    rendered_phrase = template.render(context)

    time_threshold = timezone.now() - timedelta(days=30)

    created_events = Event.objects.filter(
        creator=request.user,
        deadline_date__gte=timezone.now().date() - timedelta(days=30)
    )
    assigned_tasks = Task.objects.filter(
        assignees=request.user,
        updated_at__gte=time_threshold
    )
    sent_invitations = Invitation.objects.filter(
        sender=request.user,
        sent_at__gte=time_threshold
    )
    added_expenses = Expense.objects.filter(
        user=request.user,
        date__gte=timezone.now().date() - timedelta(days=30)
    )
    added_incomes = Income.objects.filter(
        user=request.user,
        date__gte=timezone.now().date() - timedelta(days=30)
    )

    created_tasks = Task.objects.filter(
        event__creator=request.user,
        created_at__gte=time_threshold
    )
    created_budgets = Budget.objects.filter(
        event__creator=request.user,
        created_at__gte=time_threshold
    )

    activity_list = []

    for event in created_events:
        activity_list.append({
            'type': 'event_created',
            'description': f'Создали мероприятие "{event.title}"',
            'timestamp': event.created_at,
            'related_object': event,
        })

    for task in assigned_tasks:
        activity_list.append({
            'type': 'task_assigned',
            'description': f'Назначены на задачу "{task.title}" в мероприятии "{task.event.title}"',
            'timestamp': task.created_at,
            'related_object': task,
        })

    for invitation in sent_invitations:
        activity_list.append({
            'type': 'invitation_sent',
            'description': f'Отправили приглашение на мероприятие "{invitation.event.title}". {invitation.name or invitation.email} в списке приглашенных.',
            'timestamp': invitation.sent_at,
            'related_object': invitation,
        })

    for expense in added_expenses:
        activity_list.append({
            'type': 'expense_added',
            'description': f'Добавили расход {expense.amount} на мероприятие "{expense.event.title}"',
            'timestamp': expense.created_at,
            'related_object': expense,
        })

    for income in added_incomes:
        activity_list.append({
            'type': 'income_added',
            'description': f'Добавили доход {income.amount} на мероприятие "{income.event.title}"',
            'timestamp': income.created_at,
            'related_object': income,
        })

    for task in created_tasks:
        activity_list.append({
            'type': 'task_created',
            'description': f'Создали задачу "{task.title}" для мероприятия "{task.event.title}"',
            'timestamp': task.created_at,
            'related_object': task,
        })

    for budget in created_budgets:
        activity_list.append({
            'type': 'budget_created',
            'description': f'Создали бюджет для мероприятия "{budget.event.title}"',
            'timestamp': budget.created_at,
            'related_object': budget,
        })

    activity_list.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activity = activity_list[:10]

    return render(request, 'authapp/profile.html', {
        'phrase': rendered_phrase,
        'recent_activity': recent_activity,
        'title': 'Профиль',
        'description': 'Просматривайте и редактируйте свой профиль в PlanIt! Управляйте личной информацией и настройками!',
        'keywords': 'настройки, профиль пользователя, планирование, организация мероприятий, PlanIt!, личные данные, последняя активность, безопасность, управление аккаунтом, изменить информацию.'
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен.')
            return redirect('authapp:edit_profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'authapp/edit_profile.html', {'form': form, 'title': 'Редактировать профиль',
                                                         'description': 'Редактируйте свой профиль в PlanIt! Загрузите аватар, обновите личную информацию и управляйте другими данными в профиле.',
                                                         'keywords': 'профиль, редактирование профиля, личная информация, настройки, PlanIt!, мероприятия, планирование.'})


@login_required
def upload_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile_picture = request.FILES['profile_picture']

        try:
            image_format(profile_picture)
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})

        request.user.profile_picture = profile_picture
        request.user.save()

        return JsonResponse({
            'success': True,
            'profile_picture_url': request.user.get_profile_picture()
        })
    else:
        return JsonResponse({'success': False, 'error': 'Нет файла изображения.'})


@login_required
def delete_profile_picture(request):
    user = request.user
    if user.profile_picture:
        user.profile_picture.delete()
        user.save()
        messages.success(request, 'Фотография профиля удалена.')
    else:
        messages.info(request, 'У вас нет фотографии профиля для удаления.')

    return redirect('authapp:edit_profile')
