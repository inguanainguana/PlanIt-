import mimetypes

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.core.exceptions import ValidationError

from authapp.models import User


class AuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'form-control'
            item.help_text = ''

        self.fields['password'].label = 'Пароль'


class RegForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False, label='Изображение профиля')

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password1',
            'password2',
            'profile_picture',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'form-control'
            item.help_text = ''

        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.startswith('+7('):
            raise forms.ValidationError("Номер телефона должен начинаться с +7(999)-999-99-99.")
        return phone_number


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if phone_number:
            if User.objects.exclude(pk=self.instance.pk).filter(phone_number=phone_number).exists():
                raise ValidationError("Этот номер телефона уже используется.")
            return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise ValidationError("Этот адрес электронной почты уже используется.")
            return email