from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'comment']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Город, улица, дом, квартира'}),
            'comment': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Пожелания к доставке или заказу'}),
        }