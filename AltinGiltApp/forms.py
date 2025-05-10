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
        
class RasmForm(forms.ModelForm):
    class Meta:
        model = Rasm
        fields = ['image'] # Faqat 'image' maydonini qoldiramiz. Django 'id' ni o'zi qo'shishi kerak.
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agar bu formaga bog'langan instance (mavjud Rasm obyekti) bo'lsa
        # va unda rasm allaqachon mavjud bo'lsa, 'image' maydonini majburiy qilmaslik.
        # Bu logikani inlineformset_factory o'zi bajarishi kerak, lekin har ehtimolga qarshi.
        if self.instance and self.instance.pk and self.instance.image:
            self.fields['image'].required = False