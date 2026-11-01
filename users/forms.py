import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Имя")
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия")
    email = forms.EmailField(required=True, label="Электронная почта (Email)")
    phone = forms.CharField(max_length=20, required=True, label="Контактный телефон",
                            help_text="Например: +7 (999) 123-45-67 или 89991234567")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Адрес доставки")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits_only = re.sub(r'\D', '', phone)

        if len(digits_only) != 11 or digits_only[0] not in ('7', '8'):
            raise ValidationError("Введите корректный номер мобильного телефона (11 цифр).")

        formatted_phone = f"+7{digits_only[1:]}"

        if CustomUser.objects.filter(phone=formatted_phone).exists():
            raise ValidationError("Пользователь с таким номером телефона уже зарегистрирован.")

        return formatted_phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if '@' not in email:
            raise ValidationError("Адрес электронной почты должен содержать символ @.")

        local_part, domain = email.split('@', 1)
        if len(local_part) < 2:
            raise ValidationError("Имя почтового ящика (до знака @) должно содержать не менее 2 символов.")
        if '.' not in domain or len(domain.split('.')[-1]) < 2:
            raise ValidationError("Укажите корректный почтовый домен.")

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким адресом электронной почты уже зарегистрирован.")
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
            'phone': 'Контактный телефон',
            'address': 'Адрес доставки',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits_only = re.sub(r'\D', '', phone)

        if len(digits_only) != 11 or digits_only[0] not in ('7', '8'):
            raise ValidationError("Номер телефона должен содержать 11 цифр.")

        formatted_phone = f"+7{digits_only[1:]}"

        if CustomUser.objects.filter(phone=formatted_phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Этот номер телефона уже используется другим пользователем.")

        return formatted_phone