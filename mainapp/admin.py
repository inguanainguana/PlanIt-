from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.sites.models import Site

from authapp.models import User
from mainapp.models import Event, Task, Category, TransactionCategory, Invitation, Expense, Income, Budget, FAQ, \
    SupportApplication, Review


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff',
                    'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password', 'password2'),
        }),
    )
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password') and not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['password2'] = forms.CharField(
                label='Подтверждение пароля',
                widget=forms.PasswordInput
            )
        return form

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if not change and request.POST.get('password2') != form.cleaned_data['password']:
                raise forms.ValidationError('Пароли не совпадают')
            instance.save()
        formset.save_m2m()


class InvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'status', 'name', 'sent_at', 'sender')
    list_filter = ('status', 'event', 'sent_at')
    search_fields = ('email', 'name', 'event__title')
    readonly_fields = ('confirmation_link', 'sent_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('sender',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.sender = request.user
        super().save_model(request, obj, form, change)


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'other_category', 'amount', 'date', 'event', 'user')
    list_filter = ('date', 'category', 'event', 'user')
    search_fields = ('other_category', 'event__title', 'user__username')


class IncomeAdmin(admin.ModelAdmin):
    list_display = ('category', 'other_category', 'amount', 'date', 'event', 'user')
    list_filter = ('date', 'category', 'event', 'user')
    search_fields = ('other_category', 'event__title', 'user__username')


class BudgetAdmin(admin.ModelAdmin):
    list_display = ('event', 'total_budget', 'expenses_total', 'incomes_total', 'remaining_budget')
    readonly_fields = ('expenses_total', 'incomes_total', 'remaining_budget')
    search_fields = ('event__title', 'description')


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline_date', 'location', 'category')
    list_filter = ('deadline_date', 'category')
    search_fields = ('title', 'description')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'status')
    list_filter = ('status', 'assignees')
    search_fields = ('title', 'description')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


class TransactionCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'updated_at')
    search_fields = ('question', 'answer')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class SupportApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('subject', 'message', 'user__username',
                     'email')
    readonly_fields = ('created_at', 'updated_at')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'is_visible', 'created_at')
    list_filter = ('is_visible', 'created_at')
    search_fields = ('text', 'user__username')
    ordering = ('-created_at',)


class CustomAdminSite(admin.AdminSite):
    def has_permission(self, request):
        return request.user.is_superuser


admin.site = CustomAdminSite(name='is_superuser')
admin.site.register(User, CustomUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TransactionCategory, TransactionCategoryAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Income, IncomeAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(SupportApplication, SupportApplicationAdmin)
admin.site.register(Review, ReviewAdmin)
#admin.site.register(Site)
