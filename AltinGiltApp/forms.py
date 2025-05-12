# AltinGiltApp/forms.py
from django import forms
from .models import Elon, Rasm, Shahar, Tur
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model() # Bizning CustomUser modelimizni oladi

class CustomUserCreationForm(UserCreationForm):
    # first_name ni majburiy qilish va last_name ni ixtiyoriy qilish
    first_name = forms.CharField(max_length=150, required=True, label=_("Ism"))
    last_name = forms.CharField(max_length=150, required=False, label=_("Familiya"))
    # email = forms.EmailField(required=False) # Agar email ixtiyoriy bo'lsa

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # USERNAME_FIELD 'phone_number' bo'lgani uchun, 'phone_number' ni ko'rsatish kerak
        fields = ('phone_number', 'first_name', 'last_name') # email ni olib tashladim, agar kerak bo'lsa qo'shing
        # Agar parolni ikki marta kiritish kerak bo'lsa, UserCreationForm buni o'zi qiladi

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Maydonlarga Bootstrap klasslarini qo'shish
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mb-2'
            if field_name == 'phone_number':
                field.help_text = CustomUser._meta.get_field('phone_number').help_text
                field.widget.attrs['placeholder'] = '+998XXYYYYYYY'


class CustomAuthenticationForm(AuthenticationForm):
    # Standart AuthenticationForm 'username' ni ishlatadi. Buni o'zgartirish kerak.
    username = forms.CharField(
        label=_("Telefon raqami"),
        strip=False,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control mb-2'})
    )
    # password maydoni AuthenticationForm dan keladi, unga ham class qo'shamiz
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['password'].widget.attrs['class'] = 'form-control mb-3'




class ElonForm(forms.ModelForm):
    # joylashuvi va turi endi ModelChoiceField bo'ladi
    # Ularni alohida e'lon qilish shart emas, agar standart widget va queryset yetarli bo'lsa.
    # Agar ularni moslashtirish kerak bo'lsa:
    # joylashuvi = forms.ModelChoiceField(queryset=Shahar.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    # turi = forms.ModelChoiceField(queryset=Tur.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Elon
        fields = ['nomi', 'joylashuvi', 'turi', 'narxi', 'batafsil']
        widgets = {
            'nomi': forms.TextInput(attrs={'class': 'form-control'}),
            # 'joylashuvi' va 'turi' uchun standart select widget ishlatiladi. Agar kerak bo'lsa, o'zgartirish mumkin.
            'joylashuvi': forms.Select(attrs={'class': 'form-select'}), # Explicitly defining for class
            'turi': forms.Select(attrs={'class': 'form-select'}),       # Explicitly defining for class
            'narxi': forms.NumberInput(attrs={'class': 'form-control'}),
            'batafsil': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'nomi': "E'lon nomi",
            'joylashuvi': "Joylashuvi (shahar)", # O'zgartirildi
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