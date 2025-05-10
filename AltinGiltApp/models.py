# AltinGiltApp/models.py
from django.db import models
from django.contrib.auth.models import User # Django'ning standart User modelini import qilamiz

class Elon(models.Model):
    nomi = models.CharField(max_length=200)
    joylashuvi = models.CharField(max_length=100)
    # Keling, 'turi' uchun cheklangan variantlar ro'yxatini yaratamiz
    class ElonTuri(models.TextChoices):
        UY = 'Uy', 'Uy'
        KVARTIRA = 'Kvartira', 'Kvartira'
        YER = 'Yer', 'Yer'
        # Agar kerak bo'lsa, boshqa turlarni qo'shishingiz mumkin

    turi = models.CharField(
        max_length=10,
        choices=ElonTuri.choices,
        default=ElonTuri.UY  # Standart qiymat (ixtiyoriy)
    )
    narxi = models.PositiveIntegerField() # Narx manfiy bo'lmasligi uchun
    batafsil = models.TextField()
    # Foydalanuvchi bilan bog'lash (Django User modeli bilan)
    # on_delete=models.CASCADE: Foydalanuvchi o'chirilganda uning e'lonlari ham o'chiriladi
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='elonlar')
    # Yaratilgan va yangilangan vaqtni avtomatik saqlash (ixtiyoriy, lekin foydali)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Bu metod admin panelida va boshqa joylarda obyektni oson tanish uchun ishlatiladi
        return self.nomi

    class Meta:
        # Jadval nomini aniq belgilash (ixtiyoriy)
        # db_table = 'elonlar_jadvali'
        # Tartiblash (masalan, yangilari birinchi)
        ordering = ['-created_at']



# Rasmlarni qayerga yuklashni belgilash funksiyasi (dinamik yo'l yaratish)
def elon_rasm_path(instance, filename):
    # Fayl 'media/elon_rasmlari/<elon_id>/<filename>' ko'rinishida saqlanadi
    return f'elon_rasmlari/{instance.elon.id}/{filename}'

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

    # class Meta:
    #     db_table = 'rasmlar_jadvali'