# AltinGiltApp/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin # Django'ning standart User modelini import qilamiz
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', # Yoki O'zbekiston uchun aniqroq format: r'^\+998\d{9}$'
    message=_("Telefon raqami formati noto'g'ri. Misol: '+998901234567'")
)

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, first_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('Telefon raqami kiritilishi shart'))
        if not first_name:
            raise ValueError(_('Ism kiritilishi shart'))

        # Telefon raqamini normallashtirish mumkin (masalan, + belgisini olib tashlash yoki qo'shish)
        # user = self.model(phone_number=self.normalize_email(phone_number), **extra_fields) # normalize_email o'rniga boshqa narsa
        user = self.model(phone_number=phone_number, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, first_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Superuser aktiv bo'lishi kerak

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser is_staff=True bo\'lishi kerak.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser is_superuser=True bo\'lishi kerak.'))
        
        return self.create_user(phone_number, first_name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        _('telefon raqami'), 
        max_length=17, 
        unique=True,
        validators=[phone_regex], # Validatorni qo'shdik
        help_text=_('Telefon raqamingizni +998XXXXXXXXX formatida kiriting.')
    )
    first_name = models.CharField(_('ism'), max_length=150)
    last_name = models.CharField(_('familiya'), max_length=150, blank=True) # Familiya ixtiyoriy
    
    # Django User modelidagi standart maydonlar (kerak bo'lsa)
    email = models.EmailField(_('elektron pochta'), blank=True, null=True, unique=True) # Emailni ham unique qilish mumkin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) # Yangi userlar avtomatik aktiv bo'lsinmi?
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number' # Login uchun ishlatiladigan maydon
    REQUIRED_FIELDS = ['first_name'] # createsuperuser so'raydigan maydonlar (USERNAME_FIELD dan tashqari)

    def __str__(self):
        return f"{self.first_name} ({self.phone_number})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    class Meta:
        verbose_name = _('foydalanuvchi')
        verbose_name_plural = _('foydalanuvchilar')


class Shahar(models.Model):
    nomi = models.CharField(_("Shahar nomi"), max_length=100, unique=True)
    # slug = models.SlugField(unique=True, blank=True) # Agar URL uchun kerak bo'lsa

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = _("shahar")
        verbose_name_plural = _("shaharlar")
        ordering = ['nomi']

class Tur(models.Model):
    nomi = models.CharField(_("Mulk turi nomi"), max_length=50, unique=True)
    # slug = models.SlugField(unique=True, blank=True) # Agar URL uchun kerak bo'lsa
    # description = models.TextField(_("Tavsif"), blank=True) # Qo'shimcha ma'lumot

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = _("mulk turi")
        verbose_name_plural = _("mulk turlari")
        ordering = ['nomi']



class Elon(models.Model):
    nomi = models.CharField(max_length=200)
    joylashuvi = models.ForeignKey(Shahar, on_delete=models.SET_NULL, null=True, blank=False, verbose_name=_("Joylashuvi"))
    manzil = models.CharField(_("Aniq manzil"), max_length=255, blank=True, 
                              help_text=_("Ko'cha, uy raqami, mo'ljal (ixtiyoriy)")) 
    turi = models.ForeignKey(Tur, on_delete=models.SET_NULL, null=True, blank=False, verbose_name=_("Mulk turi"))
    narxi = models.PositiveIntegerField() # Narx manfiy bo'lmasligi uchun
    batafsil = models.TextField()
    # Foydalanuvchi bilan bog'lash (Django User modeli bilan)
    # on_delete=models.CASCADE: Foydalanuvchi o'chirilganda uning e'lonlari ham o'chiriladi
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='elonlar')
    # Yaratilgan va yangilangan vaqtni avtomatik saqlash (ixtiyoriy, lekin foydali)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('Moderatsiyada')
        APPROVED = 'APPROVED', _('Tasdiqlangan')
        REJECTED = 'REJECTED', _('Rad etilgan')

    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True # Status bo'yicha tez-tez filter qilinadi
    )
    
    moderation_notes = models.TextField(
        blank=True, null=True, # Faqat rad etilganda to'ldiriladi
        verbose_name=_("Moderator izohi (rad etish sababi)")
    )

    def __str__(self):
        # Bu metod admin panelida va boshqa joylarda obyektni oson tanish uchun ishlatiladi
        return self.nomi

    class Meta:
        # Jadval nomini aniq belgilash (ixtiyoriy)
        # db_table = 'elonlar_jadvali'
        # Tartiblash (masalan, yangilari birinchi)
        ordering = ['-created_at']
        verbose_name = _('e\'lon')
        verbose_name_plural = _('e\'lonlar')



# Rasmlarni qayerga yuklashni belgilash funksiyasi (dinamik yo'l yaratish)
def elon_rasm_path(instance, filename):
    # Fayl 'media/elon_rasmlari/<elon_id>/<filename>' ko'rinishida saqlanadi
    return f'images/{instance.elon.id}/{filename}'

class Rasm(models.Model):
    # Fayl nomini saqlash shart emas, Django buni o'zi boshqaradi.
    # Agar eski fayl nomini saqlamoqchi bo'lsangiz, CharField qo'shishingiz mumkin.
    # fayl_nomi_original = models.CharField(max_length=255, blank=True) # blank=True - ixtiyoriy maydon

    # ImageField faylni fayl tizimida saqlaydi, yo'lini esa bazada
    image = models.ImageField(upload_to=elon_rasm_path)
    # Elon bilan bog'lash
    # on_delete=models.CASCADE: Elon o'chirilganda unga tegishli rasmlar ham o'chiriladi (fayl tizimidan emas, faqat bazadagi yozuv)
    # related_name='rasmlar' - Elon obyektidan uning rasmlariga oson murojaat qilish uchun (elon_obj.rasmlar.all())
    elon = models.ForeignKey(Elon, on_delete=models.CASCADE, related_name='rasmlar')

    def __str__(self):
        # Faylning asosiy nomini qaytarish
        import os
        return os.path.basename(self.image.name)

    class Meta:
        # db_table = 'rasmlar_jadvali'
        verbose_name = _('rasm')
        verbose_name_plural = _('rasmlar')