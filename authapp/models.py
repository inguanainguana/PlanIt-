import mimetypes
import re

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


def check_fio(value):
    pattern = r'^[а-яА-ЯёЁ]+$'
    if re.match(pattern, value):
        pass
    raise ValidationError('Доступны только русские символы', params={'value': value})


def image_format(value):
    valid_formats = ['image/jpeg', 'image/png']
    mime_type, _ = mimetypes.guess_type(value.name)

    if mime_type not in valid_formats:
        raise ValidationError('Неподдерживаемый формат изображения. Пожалуйста, загрузите JPEG или PNG')


class User(AbstractUser):
    username_validator = ASCIIUsernameValidator()

    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    first_name = models.CharField(verbose_name='Имя', max_length=150, validators=[RegexValidator(
        regex='^[А-Яа-яЁё]+$',
        message='Используйте только русские символы!'
    )])
    last_name = models.CharField(verbose_name='Фамилия', max_length=150, validators=[RegexValidator(
        regex='^[А-Яа-яЁё]+$',
        message='Используйте только русские символы!'
    )])
    phone_number = models.CharField(
        verbose_name='Номер телефона',
        max_length=17,
        unique=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+7\(\d{3}\)-\d{3}-\d{2}-\d{2}$',
            message='Номер телефона должен быть в формате +7(999)-999-99-99'
        )]
    )
    profile_picture = models.ImageField(verbose_name='Изображение профиля', upload_to='img_profile/',
                                        validators=[image_format], blank=True, null=True)
    email = models.EmailField(verbose_name='Email', unique=True)

    def get_profile_picture(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/media/img_profile/profile.png'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
