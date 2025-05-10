# AltinGiltApp/forms.py
from django import forms
from .models import Elon, Rasm

class ElonForm(forms.ModelForm):
    class Meta:
        model = Elon
        # Formada ko'rsatiladigan maydonlar
        fields = ['nomi', 'joylashuvi', 'turi', 'narxi', 'batafsil']
        # `user` maydoni avtomatik ravishda view'da olinadi, shuning uchun formaga kiritmaymiz
        # `created_at`, `updated_at` avtomatik to'ldiriladi

        # Maydonlarga qo'shimcha atributlar qo'shish (masalan, Bootstrap klasslari)
        widgets = {
            'nomi': forms.TextInput(attrs={'class': 'form-control'}),
            'joylashuvi': forms.TextInput(attrs={'class': 'form-control'}),
            'turi': forms.Select(attrs={'class': 'form-select'}),
            'narxi': forms.NumberInput(attrs={'class': 'form-control'}),
            'batafsil': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        # Maydonlar uchun label'larni o'zgartirish (ixtiyoriy)
        labels = {
            'nomi': "E'lon nomi",
            'joylashuvi': "Joylashuvi (shahar/tuman)",
            'turi': "Mulk turi",
            'narxi': "Narxi (so'mda)",
            'batafsil': "Batafsil ma'lumot",
        }

class RasmForm(forms.ModelForm):
    class Meta:
        model = Rasm
        # Formada faqat rasm faylini yuklash maydoni bo'ladi
        fields = ['image']
        # `elon` maydoni view'da bog'lanadi

        widgets = {
            # multiple=True ni olib tashladik. Bu yerda bitta forma bitta rasm uchun.
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'image': 'Rasm fayli'
        }