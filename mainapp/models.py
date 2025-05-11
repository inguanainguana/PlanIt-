from django.db import models
from django.db.models import Sum

from authapp.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    location = models.CharField(max_length=200, verbose_name="Место проведения")
    deadline_date = models.DateField(verbose_name="Даты дедлайна")
    event_time = models.TimeField(verbose_name="Время проведения")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', verbose_name="Создатель")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    other_category = models.ImageField(upload_to='category_icons/', default='category_icons/default_image.png',
                                       blank=True, verbose_name="Нет категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятии"

    def __str__(self):
        return self.title


class Task(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    assignees = models.ManyToManyField(User, related_name='assigned_tasks', verbose_name="Исполнители")
    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Открыта'),
            ('in_progress', 'В работе'),
            ('completed', 'Завершена'),
        ],
        default='open',
        verbose_name="Статус"
    )
    deadline = models.DateField(null=True, blank=True, verbose_name="Срок выполнения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    completed = models.BooleanField(default=False, verbose_name="Завершена")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['deadline', '-created_at']

    def __str__(self):
        return self.title


class Invitation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Мероприятие")
    email = models.EmailField(verbose_name="Email приглашённого")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает ответа'),
            ('accepted', 'Принято'),
            ('declined', 'Отклонено'),
        ],
        default='pending',
        verbose_name="Статус приглашения"
    )
    name = models.CharField(max_length=100, blank=True, verbose_name="Имя приглашённого")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время отправки")
    confirmation_link = models.URLField(verbose_name="Уникальная ссылка для подтверждения", unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Отправитель")

    class Meta:
        verbose_name = "Приглашение"
        verbose_name_plural = "Приглашения"

    def __str__(self):
        return f"Приглашение для {self.name or self.email} на {self.event.title}"


class TransactionCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория транзакции"
        verbose_name_plural = "Категории транзакций"

    def __str__(self):
        return self.name


class Expense(models.Model):
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="Категория")
    other_category = models.CharField(max_length=100, null=True, blank=True, verbose_name="Другое")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='expenses', verbose_name="Мероприятие")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Участник мероприятия")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    def __str__(self):
        return f"{self.amount} ({self.date})"


class Income(models.Model):
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="Категория")
    other_category = models.CharField(max_length=100, null=True, blank=True, verbose_name="Другое")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='incomes', verbose_name="Мероприятие")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Участник мероприятия")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Доход"
        verbose_name_plural = "Доходы"

    def __str__(self):
        return f"{self.amount} ({self.date})"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Участник мероприятия")
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='budget', verbose_name="Мероприятие")
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Общий бюджет")
    description = models.TextField(blank=True, null=True, verbose_name="Описание бюджета")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бюджет"
        verbose_name_plural = "Бюджеты"

    def __str__(self):
        return f"Бюджет для {self.event.title}"

    def expenses_total(self):
        return self.event.expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    def incomes_total(self):
        return self.event.incomes.aggregate(Sum('amount'))['amount__sum'] or 0

    def remaining_budget(self):
        return self.total_budget - self.expenses_total()


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Вопрос-ответ (FAQ)"
        verbose_name_plural = "Вопросы-ответы (FAQ)"
        ordering = ['question']

    def __str__(self):
        return self.question


class SupportApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="Пользователь")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('in_progress', 'В обработке'),
        ('closed', 'Закрыт'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заявка в поддержку"
        verbose_name_plural = "Заявки в поддержку"
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name='Текст отзыва')
    is_visible = models.BooleanField(default=False, verbose_name='Отображать на странице')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f'Отзыв от {self.user.username}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
