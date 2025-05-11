from django import forms
from django.core.exceptions import ValidationError

from authapp.models import User
from mainapp.models import Event, Task, Invitation, TransactionCategory, Income, Budget, Expense, SupportApplication, \
    Review


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'deadline_date', 'event_time', 'category']
        widgets = {
            'deadline_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'event_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }


class TaskForm(forms.ModelForm):
    assignee_usernames = forms.CharField(
        label="Логины исполнителей (через запятую)",
        required=False,
        help_text="Введите логины пользователей, которым нужно назначить задачу, разделенные запятыми."
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'status']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_assignee_usernames(self):
        usernames = self.cleaned_data['assignee_usernames'].strip()
        if not usernames:
            return []

        username_list = [u.strip() for u in usernames.split(',')]
        users = []
        for username in username_list:
            try:
                user = User.objects.get(username=username)
                users.append(user)
            except User.DoesNotExist:
                raise ValidationError(f"Пользователь с логином '{username}' не найден.")
        return users

    def save(self, commit=True, event=None):
        instance = super().save(commit=False)

        if event:
            instance.event = event

        if commit:
            instance.save()

        assignees = self.cleaned_data['assignee_usernames']
        instance.assignees.set(assignees)

        return instance


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['event', 'name', 'email', 'status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'other_category', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['category', 'other_category', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['total_budget', 'description']


class EventSelectionForm(forms.Form):
    event = forms.ModelChoiceField(queryset=None, label="Выберите мероприятие")

    def __init__(self, *args, events=None, **kwargs):
        super().__init__(*args, **kwargs)
        if events is not None:
            self.fields['event'].queryset = events


class DeletionForm(forms.Form):
    delete_budget = forms.BooleanField(required=False, label="Бюджет")


class ExpenseDeletionForm(forms.Form):
    expenses_to_delete = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите расходы для удаления"
    )

    def __init__(self, *args, expenses=None, **kwargs):
        super().__init__(*args, **kwargs)
        if expenses:
            choices = []
            for expense in expenses:
                category_name = expense.category.name if expense.category else "Без категории"
                desc = expense.other_category or category_name
                choices.append((expense.id, f"{desc} — {expense.amount} ({expense.date})"))
            self.fields['expenses_to_delete'].choices = choices


class IncomeDeletionForm(forms.Form):
    incomes_to_delete = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите доходы для удаления"
    )

    def __init__(self, *args, incomes=None, **kwargs):
        super().__init__(*args, **kwargs)
        if incomes:
            choices = []
            for income in incomes:
                category_name = income.category.name if income.category else "Без категории"
                desc = income.other_category or category_name
                choices.append((income.id, f"{desc} — {income.amount} ({income.date})"))
            self.fields['incomes_to_delete'].choices = choices


class SupportApplicationForm(forms.ModelForm):
    class Meta:
        model = SupportApplication
        fields = ['subject', 'message', 'email']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Заголовок'}),
            'message': forms.Textarea(attrs={'placeholder': 'Опишите вашу проблему или вопрос здесь'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш Email'}),
        }
        labels = {
            'subject': '',
            'message': '',
            'email': '',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['email'].required = False
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mt-4'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите ваш отзыв...',
                'rows': 4,
            }),
        }
        labels = {
            'text': '',
        }
