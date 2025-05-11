import json
import random
from decimal import Decimal
import mainapp.sitemaps as sitemaps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, message, EmailMultiAlternatives
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from planit import settings
from planit.settings import DEFAULT_FROM_EMAIL
from .utils import generate_confirmation_link

from mainapp.forms import EventForm, TaskForm, InvitationForm, ExpenseForm, IncomeForm, BudgetForm, EventSelectionForm, \
    DeletionForm, ExpenseDeletionForm, IncomeDeletionForm, SupportApplicationForm, ReviewForm
from mainapp.models import Event, Task, Invitation, Expense, Income, Budget, TransactionCategory, FAQ, Review
from django.templatetags.static import static


def index(request):
    reviews = Review.objects.filter(is_visible=True).order_by('-created_at')

    context = {
        'title': 'Главная',
        'reviews': reviews,
        "description": "Планируйте, организуйте и управляйте мероприятиями с PlanIt! - вашим универсальным инструментом для создания списков задач, координации участников и отслеживания прогресса.",
        "keywords": "мероприятия, планирование, организация, управление задачами, PlanIt!, инструменты для мероприятий, координация участников, отслеживание задач, создание мероприятий, эффективность планирования"
    }
    return render(request, 'mainapp/index.html', context)


def write_review(request):
    form_submitted = False

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user if request.user.is_authenticated else None
            review.is_visible = False
            review.save()
            form_submitted = True

            form = ReviewForm()


    else:
        form = ReviewForm()

    context = {
        'form': form,
        "title": "Написать свой отзыв",
        "description": "Поделитесь своим опытом использования PlanIt! Напишите отзыв и помогите другим пользователям лучше понять, как наше приложение может помочь в планировании мероприятий.",
        "keywords": "оставить отзыв, PlanIt!, отзывы пользователей, опыт использования, написать отзыв, оценка приложения, рекомендации, планирование мероприятий, организация мероприятий",
        'form_submitted': form_submitted,
    }
    return render(request, 'mainapp/review.html', context)


@login_required
def event_list(request):
    events = Event.objects.filter(
        Q(creator=request.user) | Q(tasks__assignees=request.user)
    ).distinct()

    search_query = request.GET.get('q')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    paginator = Paginator(events, 4)

    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    return render(request, 'mainapp/event_list.html', {'events': events, 'search_query': search_query})


@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if event.creator != request.user:
        return redirect('mainapp:event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('mainapp:event_list')
    else:
        form = EventForm(instance=event)
    context = {
        'form': form,
        'event': event,
        'title': f'Редактировать мероприятие "{event.title}"',
        'description': f'Обновите детали вашего мероприятия "{event.title}" в PlanIt! - меняйте время, место, задачи, участников и другие важные параметры',
        'keywords': 'редактирование мероприятия, изменение мероприятия, обновление мероприятия, управление мероприятием, планирование мероприятия, организация мероприятия, PlanIt!, задачи, участники, детали мероприятия, параметры мероприятия',
    }

    return render(request, 'mainapp/update_event.html', context)


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if event.creator != request.user:
        tasks = Task.objects.filter(event=event, assignees=request.user)
        for task in tasks:
            task.assignees.remove(request.user)
        return redirect('mainapp:event_list')
    else:
        event.delete()
        return redirect('mainapp:event_list')


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    tasks = event.tasks.filter(assignees=request.user)

    context = {
        'event': event,
        'tasks': tasks,
        'title': event.title,
        'description': 'Создавайте, планируйте, отслеживайте задачи и координируйте участников в PlanIt! - вашем веб-приложении для планирования и организации мероприятий.',
        'keywords': 'мероприятия, планирование, организация, задачи, PlanIt!, список мероприятий, добавление мероприятий, управление мероприятиями, координация, организация мероприятий, инструменты планирования',
    }

    return render(request, 'mainapp/event_detail.html', context)


@login_required
def task_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    open_tasks = Task.objects.filter(event=event, status='open')
    in_progress_tasks = Task.objects.filter(event=event, status='in_progress')
    completed_tasks = Task.objects.filter(event=event, status='completed')

    return render(request, 'mainapp/task_detail.html', {
        'event': event,
        'open_tasks': open_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'title': f'Задачи мероприятия:"{event.title}"',
        'description': 'Список задач по всем вашим мероприятиям в PlanIt! Отслеживайте прогресс, назначайте ответственных и координируйте работу команды для успешного планирования и организации мероприятий.',
        'keywords': 'задачи, мероприятие, список задач, управление задачами, назначение задач, отслеживание прогресса, PlanIt!, планирование задач, координация задач, организация мероприятия, задачи мероприятия',
    })


@csrf_exempt
def update_task_status(request, task_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        try:
            task = Task.objects.get(id=task_id)
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    event = task.event

    if request.user != event.creator and request.user not in task.assignees.all():
        return HttpResponseForbidden("У вас нет прав на редактирование этой задачи.")

    initial_assignee_usernames = ', '.join([user.username for user in task.assignees.all()])

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save(commit=True)
            assignees = form.cleaned_data['assignee_usernames']
            task.assignees.set(assignees)
            return redirect('mainapp:task_detail', event_id=event.id)
    else:
        form = TaskForm(instance=task, initial={'assignee_usernames': initial_assignee_usernames})

    return render(request, 'mainapp/edit_task.html',
                  {'form': form, 'task': task, 'event': event, 'title': f'Редактирование задачи:"{task.title}"',
                   'description': f'Редактируйте детали задачи "{task.title}" в мероприятии "{event.title}". Обновите описание, назначьте исполнителя, установите срок и отслеживайте прогресс в PlanIt',
                   'keywords': 'задачи, мероприятие, список задач, управление задачами, назначение задач, отслеживание прогресса, PlanIt!, планирование задач, координация задач, организация мероприятия, задачи мероприятия'})


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    event = task.event

    if request.user != event.creator and request.user not in task.assignees.all():
        return HttpResponseForbidden("У вас нет прав на удаление этой задачи.")

    task.delete()
    return redirect('mainapp:task_detail', event_id=event.id)


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            return redirect('mainapp:event_list')
    else:
        form = EventForm()

    context = {
        'form': form,
        'title': 'Добавить мероприятие',
        'description': 'Создавайте, планируйте, отслеживайте задачи и координируйте участников в PlanIt! - вашем веб-приложении для планирования и организации мероприятий.',
        'keywords': 'мероприятия, планирование, организация, задачи, PlanIt!, список мероприятий, добавление мероприятий, управление мероприятиями, координация, организация мероприятий, инструменты планирования',
    }
    return render(request, 'mainapp/create_event.html', context)


@login_required
def create_task(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=True, event=event)
            return redirect('mainapp:task_detail', event_id=event.id)
    else:
        form = TaskForm()
    return render(request, 'mainapp/create_task.html',
                  {'form': form, 'event': event, 'title': 'Добавить задачу в мероприятие',
                   'description': 'Легко добавляйте задачи к вашим мероприятиям в PlanIt! Отслеживайте прогресс, назначайте ответственных и координируйте свою команду для безупречного планирования.',
                   'keywords': 'задачи мероприятия, добавление задач, PlanIt!, планирование задач, организация задач, управление задачами, мероприятия, планирование мероприятий, организация мероприятий, список задач, инструменты планирования', })


def send_invitation(request):
    events = Event.objects.filter(
        Q(creator=request.user) | Q(tasks__assignees=request.user)
    ).distinct()

    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name', '')
        event_id = request.POST.get('event')
        event = Event.objects.get(id=event_id)

        confirmation_link = generate_confirmation_link()

        invitation = Invitation.objects.create(
            event=event,
            email=email,
            name=name,
            confirmation_link=confirmation_link,
            sender=request.user,
        )

        subject = 'Приглашение на мероприятие!'
        html_content = render_to_string('other/invitation_email.html', {
            'name': name,
            'event_title': event.title,
            'confirmation_link': f'http://127.0.0.1:8000/invitations/confirm/{invitation.confirmation_link}/'
        })

        email_message = EmailMultiAlternatives(subject, '', DEFAULT_FROM_EMAIL, [email])
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)

        messages.success(request, 'Приглашение успешно отправлено!')
        return redirect('mainapp:invitation_list')

    return render(request, 'mainapp/send_invitation.html', {'events': events, 'title': 'Отправить приглашение',
                                                            'description': 'Легко создавайте и управляйте списком гостей для вашего мероприятия с помощью PlanIt! ',
                                                            'keywords': 'список гостей, управление гостями, приглашения, добавление гостей, PlanIt!, планирование мероприятий, организация мероприятий, список участников.', })


def confirm_invitation(request, confirmation_link):
    try:
        invitation = Invitation.objects.get(confirmation_link=confirmation_link)
        invitation.status = 'accepted'
        invitation.save()

        event = invitation.event
        messages.success(request, 'Ваше участие успешно подтверждено!')

        return render(request, 'mainapp/confirmation_success.html', {'event': event, 'title': 'Подтверждение участия',
                                                                     'description': 'Подтвердите свое участие в мероприятии с помощью PlanIt! - удобного веб-приложения для управления списком гостей и организации событий. Узнайте, кто будет с вами и не пропустите ни одной детали!',
                                                                     'keywords': 'мероприятия, планирование, организация, задачи, PlanIt!, список гостей, управление мероприятиями, координация, организация мероприятий, инструменты планирования', })

    except Invitation.DoesNotExist:
        messages.error(request, 'Ссылка для подтверждения недействительна.')
        return render(request, 'mainapp/confirmation_error.html', {'title': 'Недействительная ссылка на участие',
                                                                   'description': 'К сожалению, предоставленная вами ссылка на приглашение недействительна. Пожалуйста, убедитесь, что ссылка верна, или обратитесь к организатору мероприятия за новой.',
                                                                   'keywords': 'недействительная ссылка, приглашение, мероприятие, ошибка, PlanIt!, список гостей, управление мероприятиями, координация, организация мероприятий, инструменты планирования', })


def invitation_list(request):
    search_query = request.GET.get('q')
    invitations = Invitation.objects.filter(
        Q(sender=request.user) | Q(event__tasks__assignees=request.user)
    ).distinct()

    if search_query:
        invitations = invitations.filter(
            Q(event__title__icontains=search_query) | Q(name__icontains=search_query))

    paginator = Paginator(invitations, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mainapp/invitation_list.html', {
        'invitations': page_obj,
        'search_query': search_query,
        'events': page_obj,
        'title': 'Список гостей',
        'description': 'Управляйте списком гостей в PlanIt! Добавляйте, редактируйте и отправляйте приглашения.',
        'keywords': 'список гостей, гости, приглашения, управление гостями, список приглашенных, организация мероприятий, планирование мероприятий, PlanIt! координация, организация мероприятий, инструменты планирования',
    })


@login_required
def edit_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    events = Event.objects.filter(
        Q(creator=request.user) | Q(tasks__assignees=request.user)
    ).distinct()

    if request.method == 'POST':
        form = InvitationForm(request.POST, instance=invitation)
        if form.is_valid():
            form.save()
            return redirect('mainapp:invitation_list')
    else:
        form = InvitationForm(instance=invitation)

    context = {
        'form': form,
        'events': events,
        'title': 'Редактирование приглашения',
        'description': 'Легко обновляйте список гостей для вашего мероприятия в PlanIt! Добавляйте, редактируйте и удаляйте приглашенных, чтобы всегда иметь актуальную информацию.',
        'keywords': 'редактирование списка гостей, управление списком гостей, обновление списка гостей, добавление гостей, PlanIt!, планирование мероприятий, организация мероприятий, список участников.'
    }
    return render(request, 'mainapp/edit_invitation.html', context)


@login_required
def delete_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    event = invitation.event

    if request.user != event.creator and request.user != invitation.sender:
        tasks = Task.objects.filter(event=event, assignees=request.user)
        if not tasks.exists():
            return HttpResponseForbidden("У вас нет прав на удаление этого приглашения.")

    invitation.delete()
    return redirect('mainapp:invitation_list')


def calculate_category_data(queryset):
    category_data = (
        queryset
        .values('category__name', 'other_category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    labels = []
    data = []

    for item in category_data:
        category_name = item['category__name'] or item['other_category'] or 'Другое'
        total = item['total']
        if total is not None:
            labels.append(category_name)
            data.append(float(total))
    return labels, data


@login_required
def add_expense(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    categories = TransactionCategory.objects.all()
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.event = event
            expense.user = request.user
            expense.save()
            return redirect(
                reverse('mainapp:budget_list') + f'?event_id={event_id}')
    else:
        form = ExpenseForm()
    return render(request, 'mainapp/add_expense.html', {
        'form': form,
        'event': event,
        'categories': categories,
        'title': 'Добавить расход',
        'description': 'Добавьте доходы вашего мероприятия с помощью PlanIt! Легко отслеживайте все поступления, оптимизируйте финансовое планирование и обеспечьте успешное проведение мероприятий.',
        'keywords': 'добавление дохода, управление финансами, учет доходов, планирование бюджета, отслеживание доходов, финансовый учет, доходы мероприятия, оптимизация бюджета, финансовый контроль, управление мероприятиями'
    })


@login_required
def add_income(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    categories = TransactionCategory.objects.all()
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.event = event
            income.user = request.user
            income.save()
            return redirect(
                reverse('mainapp:budget_list') + f'?event_id={event_id}')
    else:
        form = IncomeForm()
    return render(request, 'mainapp/add_income.html',
                  {'form': form, 'event': event, 'categories': categories, 'title': 'Добавить доход',
                   'description': 'Добавьте расходы вашего мероприятия с помощью PlanIt! Легко отслеживайте все финансовые траты, контролируйте бюджет и обеспечьте успешное проведение мероприятий.',
                   'keywords': 'добавление расхода, управление финансами, учет расходов, планирование бюджета, контроль затрат, финансовый учет, расходы мероприятия, отслеживание расходов, оптимизация бюджета, финансовый контроль'})


@login_required
def add_budget(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            existing_budget = Budget.objects.filter(event=event).first()
            if existing_budget:
                form.add_error(None, 'Бюджет для этого мероприятия уже существует.')
            else:
                budget = form.save(commit=False)
                budget.event = event
                budget.user = request.user
                budget.save()
                return redirect(reverse('mainapp:budget_list') + f'?event_id={event_id}')
    else:
        form = BudgetForm(initial={'event': event})

    return render(request, 'mainapp/add_budget.html', {
        'form': form,
        'event': event,
        'title': 'Добавить бюджет',
        'description': 'Добавьте и управляйте бюджетом вашего мероприятия с помощью PlanIt! Легко отслеживайте расходы, контролируйте финансовые потоки и обеспечьте успешное проведение мероприятий в рамках запланированного бюджета.',
        'keywords': 'добавление бюджета, управление финансами, планирование бюджета, контроль расходов, бюджет мероприятия, финансовый план, инструменты бюджета, PlanIt!, оптимизация затрат, учет расходов, создание бюджета',
    })


@login_required
def edit_budget(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    budget = get_object_or_404(Budget, event=event)

    if budget.user != request.user and event.creator != request.user:
        messages.error(request, "У вас нет прав на редактирование этого бюджета.")
        return redirect(reverse('mainapp:budget_list') + f'?event_id={event_id}')

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.event = event
            budget.save()
            return redirect(reverse('mainapp:budget_list') + f'?event_id={event_id}')
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'mainapp/edit_budget.html', {
        'form': form,
        'event': event,
        'budget': budget,
        'title': 'Редактировать бюджет',
        'description': 'Легко редактируйте бюджет вашего мероприятия с помощью PlanIt! Обновляйте расходы, вносите изменения и оптимизируйте финансовое планирование для успешного проведения мероприятий.',
        'keywords': 'редактирование бюджета, управление финансами, корректировка бюджета, обновление расходов, планирование бюджета, контроль затрат, PlanIt!, оптимизация бюджета, управление мероприятиями, финансовый контроль, изменение бюджета',
    })


@login_required
def budget_list(request):
    events = Event.objects.filter(
        Q(creator=request.user) | Q(tasks__assignees=request.user)
    ).distinct()
    form = EventSelectionForm(events=events)
    event_id = request.GET.get('event_id')
    expenses_data = {}
    incomes_data = {}
    event_name = None
    budget = None
    total_expenses = 0
    total_incomes = 0
    selected_event = None
    deletion_form = DeletionForm()
    expenses = []
    incomes = []

    if event_id:
        try:
            selected_event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            selected_event = None
            event_id = None

        if selected_event:
            event_name = selected_event.title
            budget = Budget.objects.filter(event=selected_event).first()
            total_expenses = Expense.objects.filter(event=selected_event).aggregate(total=Sum('amount'))['total'] or 0
            total_incomes = Income.objects.filter(event=selected_event).aggregate(total=Sum('amount'))['total'] or 0
            expenses = Expense.objects.filter(event=selected_event).values('category__name', 'other_category', 'id',
                                                                           'amount', 'date', 'category').annotate(
                total=Sum('amount'))
            incomes = Income.objects.filter(event=selected_event).values('category__name', 'other_category', 'id',
                                                                         'amount', 'date', 'category').annotate(
                total=Sum('amount'))

            for item in expenses:
                category_name = item['category__name']
                other_category = item['other_category']
                total = float(item['total'])
                if category_name:
                    expenses_data[category_name] = expenses_data.get(category_name, 0) + total
                elif other_category:
                    expenses_data[other_category] = expenses_data.get(other_category, 0) + total
                else:
                    expenses_data['Без категории'] = expenses_data.get('Без категории', 0) + total

            for item in incomes:
                category_name = item['category__name']
                other_category = item['other_category']
                total = float(item['total'])
                if category_name:
                    incomes_data[category_name] = incomes_data.get(category_name, 0) + total
                elif other_category:
                    incomes_data[other_category] = incomes_data.get(other_category, 0) + total
                else:
                    incomes_data['Без категории'] = incomes_data.get('Без категории', 0) + total

            form = EventSelectionForm(initial={'event': selected_event}, events=events)

    elif request.method == 'POST':
        form = EventSelectionForm(request.POST, events=events)
        if form.is_valid():
            event = form.cleaned_data['event']
            event_id = event.id
            event_name = event.title
            budget = Budget.objects.filter(event=event).first()
            total_expenses = Expense.objects.filter(event=event).aggregate(total=Sum('amount'))['total'] or 0
            total_incomes = Income.objects.filter(event=event).aggregate(total=Sum('amount'))['total'] or 0
            expenses = Expense.objects.filter(event=event).values('category__name', 'other_category', 'id', 'amount',
                                                                  'date', 'category').annotate(total=Sum('amount'))
            incomes = Income.objects.filter(event=event).values('category__name', 'other_category', 'id', 'amount',
                                                                'date', 'category').annotate(total=Sum('amount'))

            for item in expenses:
                category_name = item['category__name']
                other_category = item['other_category']
                total = float(item['total'])
                if category_name:
                    expenses_data[category_name] = expenses_data.get(category_name, 0) + total
                elif other_category:
                    expenses_data[other_category] = expenses_data.get(other_category, 0) + total
                else:
                    expenses_data['Без категории'] = expenses_data.get('Без категории', 0) + total

            for item in incomes:
                category_name = item['category__name']
                other_category = item['other_category']
                total = float(item['total'])
                if category_name:
                    incomes_data[category_name] = incomes_data.get(category_name, 0) + total
                elif other_category:
                    incomes_data[other_category] = incomes_data.get(other_category, 0) + total
                else:
                    incomes_data['Без категории'] = incomes_data.get('Без категории', 0) + total

    context = {
        'form': form,
        'event_id': event_id,
        'event_name': event_name,
        'expenses_data': expenses_data,
        'incomes_data': incomes_data,
        'budget': budget,
        'total_expenses': total_expenses,
        'total_incomes': total_incomes,
        'deletion_form': deletion_form,
        'expenses': expenses,
        'incomes': incomes,
        'title': 'Бюджет',
        'description': 'Эффективно управляйте бюджетом ваших мероприятий с помощью PlanIt! Оптимизируйте расходы, отслеживайте финансовые потоки и обеспечьте успешное проведение мероприятий с минимальными затратами.',
        'keywords': 'бюджет, управление бюджетом, планирование мероприятий, контроль затрат, финансовое планирование, оптимизация бюджета, расходы на мероприятия, PlanIt!, инструменты управления, успешные мероприятия',

    }

    return render(request, 'mainapp/budget_list.html', context)


@login_required
def delete_data(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_creator = event.creator == request.user

    if request.method == 'POST':
        if 'delete_budget' in request.POST:
            try:
                budget = Budget.objects.get(event=event)
                if is_creator or budget.user == request.user:
                    budget.delete()
                    messages.success(request, "Бюджет успешно удален.")
                else:
                    messages.error(request, "У вас нет прав для удаления этого бюджета.")
            except Budget.DoesNotExist:
                messages.info(request, "Бюджет не найден.")
            except Exception as e:
                messages.error(request, f"Произошла ошибка при удалении бюджета: {e}")
            return redirect(reverse('mainapp:budget_list') + f'?event_id={event_id}')

        selected_expense_ids = request.POST.getlist('selected_expenses')
        if selected_expense_ids:
            try:
                expenses_qs = Expense.objects.filter(event=event, id__in=selected_expense_ids)
                if not is_creator:
                    expenses_qs = expenses_qs.filter(user=request.user)
                deleted_count = expenses_qs.count()
                expenses_qs.delete()
                if deleted_count > 0:
                    messages.success(request, f"Успешно удалено {deleted_count} расходов.")
                else:
                    messages.info(request, "Нет расходов для удаления или недостаточно прав.")
            except Exception as e:
                messages.error(request, f"Произошла ошибка при удалении расходов: {e}")
            return redirect(reverse('mainapp:budget_list') + f'?event_id={event_id}')

        selected_income_ids = request.POST.getlist('selected_incomes')
        if selected_income_ids:
            try:
                incomes_qs = Income.objects.filter(event=event, id__in=selected_income_ids)
                if not is_creator:
                    incomes_qs = incomes_qs.filter(user=request.user)
                deleted_count = incomes_qs.count()
                incomes_qs.delete()
                if deleted_count > 0:
                    messages.success(request, f"Успешно удалено {deleted_count} доходов.")
                else:
                    messages.info(request, "Нет доходов для удаления или недостаточно прав.")
            except Exception as e:
                messages.error(request, f"Произошла ошибка при удалении доходов: {e}")
            return redirect(reverse('mainapp:budget_list') + f'?event_id={event_id}')

    expenses = Expense.objects.filter(event=event)
    incomes = Income.objects.filter(event=event)
    try:
        budget = Budget.objects.get(event=event)
    except Budget.DoesNotExist:
        budget = None

    context = {
        'event': event,
        'expenses': expenses,
        'incomes': incomes,
        'is_creator': is_creator,
        'budget': budget,
    }

    return redirect(context, reverse('mainapp:budget_list') + f'?event_id={event_id}')


def support_view(request):
    search_query = request.GET.get('q', '')
    support_ticket_form = SupportApplicationForm()
    submitted_successfully = False

    all_faqs_count = FAQ.objects.count()
    if all_faqs_count > 0:
        random_faqs = random.sample(list(FAQ.objects.all()), min(5, all_faqs_count))
    else:
        random_faqs = []

    if search_query:
        faqs = FAQ.objects.filter(Q(question__icontains=search_query) | Q(answer__icontains=search_query))
    else:
        faqs = FAQ.objects.none()

    if request.method == 'POST':
        support_ticket_form = SupportApplicationForm(request.POST)
        if support_ticket_form.is_valid():
            ticket = support_ticket_form.save()

            subject = 'Ваша заявка принята!'
            email = ticket.email if ticket.email else request.user.email if request.user.is_authenticated else None

            if email:
                html_content = render_to_string('other/support_confirmation.html', {
                    'ticket': ticket,
                })

                email_message = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
                email_message.attach_alternative(html_content, "text/html")
                email_message.send(fail_silently=True)

            submitted_successfully = True

    context = {
        'faqs': faqs,
        'random_faqs': random_faqs,
        'search_query': search_query,
        'support_ticket_form': support_ticket_form,
        'submitted_successfully': submitted_successfully,
        'title': 'Поддержка',
        'description': 'Нужна помощь с PlanIt!? Найдите ответы на часто задаваемые вопросы, узнайте, как пользоваться функциями приложения, или свяжитесь с нашей службой поддержки, чтобы решить вашу проблему.',
        'keywords': 'PlanIt!, поддержка, помощь, база знаний, FAQ, часто задаваемые вопросы, руководство пользователя, как пользоваться, планирование мероприятий, организация мероприятий',
    }
    return render(request, 'mainapp/support.html', context)


def all_faqs_view(request):
    search_query = request.GET.get('q', '')
    support_ticket_form = SupportApplicationForm()
    submitted_successfully = False
    faqs_to_display = FAQ.objects.none()

    if search_query:
        faqs_to_display = FAQ.objects.filter(
            Q(question__icontains=search_query) | Q(answer__icontains=search_query)
        )
        is_search_results = True
    else:
        is_search_results = False
        faqs_to_display = FAQ.objects.all()

    if request.method == 'POST':
        support_ticket_form = SupportApplicationForm(request.POST)
        if support_ticket_form.is_valid():
            ticket = support_ticket_form.save()

            subject = 'Ваша заявка принята!'
            email = ticket.email if ticket.email else request.user.email if request.user.is_authenticated else None

            if email:
                html_content = render_to_string('other/support_confirmation.html', {
                    'ticket': ticket,
                })

                email_message = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
                email_message.attach_alternative(html_content, "text/html")
                email_message.send(fail_silently=True)

            submitted_successfully = True
        else:
            print(support_ticket_form.errors)

    context = {
        'faqs': faqs_to_display,
        'search_query': search_query,
        'is_search_results': is_search_results,
        'support_ticket_form': support_ticket_form,
        'submitted_successfully': submitted_successfully,
        'title': 'Поддержка',
        'description': 'Нужна помощь с PlanIt!? Найдите ответы на часто задаваемые вопросы, узнайте, как пользоваться функциями приложения, или свяжитесь с нашей службой поддержки, чтобы решить вашу проблему.',
        'keywords': 'PlanIt!, поддержка, помощь, база знаний, FAQ, часто задаваемые вопросы, руководство пользователя, как пользоваться, планирование мероприятий, организация мероприятий',
    }

    return render(request, 'mainapp/all_answers.html', context)



