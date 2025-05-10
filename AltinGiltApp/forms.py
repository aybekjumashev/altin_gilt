# AltinGiltApp/forms.py
from django import forms
from .models import Elon, Rasm


class ElonForm(forms.ModelForm):
    class Meta:
        model = Elon
        fields = ['nomi', 'joylashuvi', 'turi', 'narxi', 'batafsil'] # status va moderation_notes olib tashlandi
        widgets = {
            'nomi': forms.TextInput(attrs={'class': 'form-control'}),
            'joylashuvi': forms.TextInput(attrs={'class': 'form-control'}),
            'turi': forms.Select(attrs={'class': 'form-select'}),
            'narxi': forms.NumberInput(attrs={'class': 'form-control'}),
            'batafsil': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'nomi': "E'lon nomi",
            'joylashuvi': "Joylashuvi (shahar/tuman)",
            'turi': "Mulk turi",
            'narxi': "Narxi (so'mda)",
            'batafsil': "Batafsil ma'lumot",
        }


# RasmForm o'zgarishsiz qoladi
class RasmForm(forms.ModelForm):
    class Meta:
        model = Rasm
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'image': 'Rasm fayli'
        }