# Generated by Django 5.2 on 2025-05-09 07:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='category_icons/', verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255, verbose_name='Вопрос')),
                ('answer', models.TextField(verbose_name='Ответ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Вопрос-ответ (FAQ)',
                'verbose_name_plural': 'Вопросы-ответы (FAQ)',
                'ordering': ['question'],
            },
        ),
        migrations.CreateModel(
            name='TransactionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название категории')),
            ],
            options={
                'verbose_name': 'Категория транзакции',
                'verbose_name_plural': 'Категории транзакций',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('location', models.CharField(max_length=200, verbose_name='Место проведения')),
                ('deadline_date', models.DateField(verbose_name='Даты дедлайна')),
                ('event_time', models.TimeField(verbose_name='Время проведения')),
                ('other_category', models.ImageField(blank=True, default='category_icons/default_image.png', upload_to='category_icons/', verbose_name='Нет категории')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.category', verbose_name='Категория')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_events', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятии',
            },
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_budget', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Общий бюджет')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание бюджета')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Участник мероприятия')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='budget', to='mainapp.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Бюджет',
                'verbose_name_plural': 'Бюджеты',
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email приглашённого')),
                ('status', models.CharField(choices=[('pending', 'Ожидает ответа'), ('accepted', 'Принято'), ('declined', 'Отклонено')], default='pending', max_length=20, verbose_name='Статус приглашения')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='Имя приглашённого')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время отправки')),
                ('confirmation_link', models.URLField(unique=True, verbose_name='Уникальная ссылка для подтверждения')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.event', verbose_name='Мероприятие')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Отправитель')),
            ],
            options={
                'verbose_name': 'Приглашение',
                'verbose_name_plural': 'Приглашения',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст отзыва')),
                ('is_visible', models.BooleanField(default=False, verbose_name='Отображать на странице')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.CreateModel(
            name='SupportApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('subject', models.CharField(max_length=200, verbose_name='Тема')),
                ('message', models.TextField(verbose_name='Сообщение')),
                ('status', models.CharField(choices=[('open', 'Открыт'), ('in_progress', 'В обработке'), ('closed', 'Закрыт')], default='open', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заявка в поддержку',
                'verbose_name_plural': 'Заявки в поддержку',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('status', models.CharField(choices=[('open', 'Открыта'), ('in_progress', 'В работе'), ('completed', 'Завершена')], default='open', max_length=20, verbose_name='Статус')),
                ('deadline', models.DateField(blank=True, null=True, verbose_name='Срок выполнения')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('completed', models.BooleanField(default=False, verbose_name='Завершена')),
                ('assignees', models.ManyToManyField(related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Исполнители')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='mainapp.event')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
                'ordering': ['deadline', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other_category', models.CharField(blank=True, max_length=100, null=True, verbose_name='Другое')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('date', models.DateField(verbose_name='Дата')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incomes', to='mainapp.event', verbose_name='Мероприятие')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Участник мероприятия')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.transactioncategory', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Доход',
                'verbose_name_plural': 'Доходы',
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other_category', models.CharField(blank=True, max_length=100, null=True, verbose_name='Другое')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('date', models.DateField(verbose_name='Дата')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='mainapp.event', verbose_name='Мероприятие')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Участник мероприятия')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.transactioncategory', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Расход',
                'verbose_name_plural': 'Расходы',
            },
        ),
    ]
