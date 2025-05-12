# AltinGiltApp/forms.py
from django import forms
from .models import Elon, Rasm, Shahar, Tur
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model() # Bizning CustomUser modelimizni oladi


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label=_("Ismingiz"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("To'liq ismingizni kiriting")})
    )
    email_or_phone = forms.CharField( # Email yoki telefon bo'lishi mumkin
        max_length=100,
        label=_("Telefon raqamingiz"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("+998 XX YYY ZZZZ")})
    )
    subject = forms.CharField(
        max_length=150,
        label=_("Mavzu"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Xabar mavzusi")})
    )
    message = forms.CharField(
        label=_("Xabar matni"),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _("Xabaringizni shu yerga yozing...")})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Viewdan user'ni olamiz
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.first_name
            self.fields['email_or_phone'].initial = user.email or user.phone_number
            # Bu maydonlarni readonly qilish ham mumkin, agar foydalanuvchi kirgan bo'lsa
            # self.fields['name'].widget.attrs['readonly'] = True
            # self.fields['email_or_phone'].widget.attrs['readonly'] = True



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



class CustomUserChangeForm(forms.ModelForm):
    # email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control mb-2'}))
    # Agar parolni ham shu formadan o'zgartirishni xohlasangiz, bu tavsiya etilmaydi.
    # Parol uchun alohida PasswordChangeForm ishlatgan ma'qul.

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email') # Tahrirlanadigan maydonlar
        # Telefon raqamini (USERNAME_FIELD) bu formadan o'zgartirishga ruxsat bermaymiz.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Maydonlarga Bootstrap klasslarini qo'shish
        self.fields['first_name'].widget.attrs.update({'class': 'form-control mb-2', 'placeholder': _("Ismingiz")})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control mb-2', 'placeholder': _("Familiyangiz (ixtiyoriy)")})
        self.fields['email'].widget.attrs.update({'class': 'form-control mb-2', 'placeholder': _("example@mail.com (ixtiyoriy)")})
        
        # Agar maydonlar modelda 'blank=True' bo'lmasa, 'required=False' ni bu yerda o'rnatish kerak
        self.fields['last_name'].required = False
        self.fields['email'].required = False # Modelda null=True, blank=True bo'lishi kerak
        

class ElonForm(forms.ModelForm):
    # joylashuvi va turi endi ModelChoiceField bo'ladi
    # Ularni alohida e'lon qilish shart emas, agar standart widget va queryset yetarli bo'lsa.
    # Agar ularni moslashtirish kerak bo'lsa:
    # joylashuvi = forms.ModelChoiceField(queryset=Shahar.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    # turi = forms.ModelChoiceField(queryset=Tur.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Elon
        fields = ['nomi', 'joylashuvi', 'manzil', 'turi', 'narxi', 'batafsil']
        widgets = {
            'nomi': forms.TextInput(attrs={'class': 'form-control'}),
            # 'joylashuvi' va 'turi' uchun standart select widget ishlatiladi. Agar kerak bo'lsa, o'zgartirish mumkin.
            'joylashuvi': forms.Select(attrs={'class': 'form-select'}), # Explicitly defining for class
            'manzil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Masalan, Amir Temur ko'chasi, 15-uy")}), # Yangi widget
            'turi': forms.Select(attrs={'class': 'form-select'}),       # Explicitly defining for class
            'narxi': forms.NumberInput(attrs={'class': 'form-control'}),
            'batafsil': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'nomi': _("E'lon sarlavhasi"), # Verbose_name dan foydalanish
            'joylashuvi': _("Shahar/Tuman"),
            'manzil': _("Aniq manzil"), # Yangi label
            'turi': _("Mulk turi"),
            'narxi': _("Narxi (so'mda)"),
            'batafsil': _("Batafsil ma'lumot"),
        }
        help_texts = { # Agar modelda help_text bo'lsa, bu shart emas, lekin override qilish mumkin
            'manzil': Elon._meta.get_field('manzil').help_text,
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