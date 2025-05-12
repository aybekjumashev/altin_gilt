# AltinGiltApp/management/commands/create_dummy_data.py
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from AltinGiltApp.models import Elon, Rasm, Shahar, Tur # Modellaringizni import qiling
from faker import Faker # Faker kutubxonasini import qilamiz
from django.utils import timezone
from django.core.files.base import ContentFile # Rasm uchun
from io import BytesIO # Rasm uchun
from PIL import Image as PILImage # Rasm yaratish uchun Pillow
import os
from django.conf import settings
from ...forms import ElonForm

CustomUser = get_user_model()
fake = Faker(['uz_UZ', 'ru_RU', 'en_US']) # O'zbek, Rus, Ingliz tillarida ma'lumotlar uchun

class Command(BaseCommand):
    help = 'Kerakli miqdorda test uchun e\'lonlar va boshqa ma\'lumotlarni yaratadi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Yaratiladigan tasodifiy foydalanuvchilar soni'
        )
        parser.add_argument(
            '--shaharlar',
            type=int,
            default=5, # Yoki mavjudlarini ishlatish uchun 0
            help='Yaratiladigan tasodifiy shaharlar soni (agar 0 bo\'lsa, mavjudlari ishlatiladi)'
        )
        parser.add_argument(
            '--turlar',
            type=int,
            default=3, # Yoki mavjudlarini ishlatish uchun 0
            help='Yaratiladigan tasodifiy mulk turlari soni (agar 0 bo\'lsa, mavjudlari ishlatiladi)'
        )
        parser.add_argument(
            '--elonlar',
            type=int,
            default=20,
            help='Har bir foydalanuvchi uchun yaratiladigan maksimal e\'lonlar soni'
        )
        parser.add_argument(
            '--rasmlar',
            type=int,
            default=5,
            help='Har bir e\'lon uchun yaratiladigan maksimal rasmlar soni'
        )
        parser.add_argument(
            '--clear',
            action='store_true', # Agar bu flag berilsa, true bo'ladi
            help='Yangi ma\'lumotlar qo\'shishdan oldin mavjud Elon va Rasm ma\'lumotlarini o\'chirish'
        )


    def handle(self, *args, **options):
        num_users = options['users']
        num_shaharlar = options['shaharlar']
        num_turlar = options['turlar']
        max_elonlar_per_user = options['elonlar']
        max_rasmlar_per_elon = options['rasmlar']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Mavjud Elon va Rasm ma\'lumotlari o\'chirilmoqda...'))
            Rasm.objects.all().delete() # Avval rasmlarni o'chiramiz (FK tufayli)
            Elon.objects.all().delete()
            # Agar kerak bo'lsa, Shahar va Tur ni ham o'chirish mumkin (agar num_shaharlar > 0 bo'lsa)
            # Shahar.objects.all().delete()
            # Tur.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Mavjud Elon va Rasm ma\'lumotlari o\'chirildi.'))


        # Foydalanuvchilarni yaratish yoki mavjudlarini olish
        users = list(CustomUser.objects.all())
        if not users or len(users) < num_users :
            self.stdout.write(f'{num_users} ta yangi foydalanuvchi yaratilmoqda...')
            for i in range(num_users - len(users)):
                phone = f'+9989{random.randint(0,9)}{random.randint(1000000, 9999999)}'
                try:
                    user = CustomUser.objects.create_user(
                        phone_number=phone,
                        first_name=fake.first_name(),
                        last_name=fake.last_name() if random.choice([True, False]) else '',
                        password='password123'
                    )
                    users.append(user)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Foydalanuvchi {phone} yaratishda xato: {e}"))
            self.stdout.write(self.style.SUCCESS(f'Foydalanuvchilar yaratildi/olindi.'))
        
        if not users:
            self.stdout.write(self.style.ERROR("Foydalanuvchilar topilmadi yoki yaratilmadi. E'lonlar qo'shib bo'lmaydi."))
            return

        # Shaharlarni yaratish yoki mavjudlarini olish
        shaharlar = list(Shahar.objects.all())
        if num_shaharlar > 0 and (not shaharlar or len(shaharlar) < num_shaharlar):
            self.stdout.write(f'{num_shaharlar} ta yangi shahar yaratilmoqda...')
            shahar_nomlari = ["Toshkent", "Samarqand", "Buxoro", "Xiva", "Nukus", "Andijon", "Farg'ona", "Namangan", "Qarshi", "Termiz", "Urganch", "Guliston", "Jizzax", "Navoiy"]
            random.shuffle(shahar_nomlari)
            for i in range(num_shaharlar):
                nom = fake.city() if not shahar_nomlari else shahar_nomlari[i % len(shahar_nomlari)]
                try:
                    shahar, created = Shahar.objects.get_or_create(nomi=nom)
                    if created and shahar not in shaharlar:
                         shaharlar.append(shahar)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Shahar '{nom}' yaratishda xato: {e}"))
            self.stdout.write(self.style.SUCCESS('Shaharlar yaratildi/olindi.'))
        
        if not shaharlar:
            self.stdout.write(self.style.ERROR("Shaharlar topilmadi yoki yaratilmadi. E'lonlar qo'shib bo'lmaydi."))
            return

        # Turlarni yaratish yoki mavjudlarini olish
        turlar = list(Tur.objects.all())
        if num_turlar > 0 and (not turlar or len(turlar) < num_turlar):
            self.stdout.write(f'{num_turlar} ta yangi mulk turi yaratilmoqda...')
            tur_nomlari = ["Kvartira", "Hovli Uy", "Yer Uchastkasi", "Dacha", "Noturar Joy", "Ofis", "Do'kon"]
            random.shuffle(tur_nomlari)
            for i in range(num_turlar):
                nom = tur_nomlari[i % len(tur_nomlari)]
                try:
                    tur, created = Tur.objects.get_or_create(nomi=nom)
                    if created and tur not in turlar:
                        turlar.append(tur)
                except Exception as e:
                     self.stdout.write(self.style.ERROR(f"Tur '{nom}' yaratishda xato: {e}"))
            self.stdout.write(self.style.SUCCESS('Mulk turlari yaratildi/olindi.'))

        if not turlar:
            self.stdout.write(self.style.ERROR("Mulk turlari topilmadi yoki yaratilmadi. E'lonlar qo'shib bo'lmaydi."))
            return

        # E'lonlarni yaratish
        self.stdout.write('E\'lonlar yaratilmoqda...')
        elon_count = 0
        for user_obj in users:
            num_elonlar_for_this_user = random.randint(1, max_elonlar_per_user)
            for _ in range(num_elonlar_for_this_user):
                shahar_obj = random.choice(shaharlar)
                tur_obj = random.choice(turlar)
                
                elon_nomi = f"{tur_obj.nomi} {shahar_obj.nomi}da, {random.randint(2,5)} xonali"
                if tur_obj.nomi == "Yer Uchastkasi":
                    elon_nomi = f"{random.randint(4,10)} sotix yer {shahar_obj.nomi}da"

                try:
                    elon = Elon.objects.create(
                        user=user_obj,
                        nomi=elon_nomi,
                        joylashuvi=shahar_obj,
                        manzil=fake.street_address(),
                        turi=tur_obj,
                        narxi=random.randint(200, 2000) * 1000000, # 200 mln dan 2 mlrd gacha
                        batafsil=fake.paragraph(nb_sentences=random.randint(5,15)),
                        status=random.choice([Elon.StatusChoices.APPROVED, Elon.StatusChoices.PENDING, Elon.StatusChoices.REJECTED])
                    )
                    elon_count +=1

                    # Rasmlarni yaratish
                    num_rasmlar = random.randint(0, max_rasmlar_per_elon)
                    if elon.status == Elon.StatusChoices.APPROVED and num_rasmlar < ElonForm.Meta.model._meta.get_field('rasmlar').field.remote_field.limit_choices_to.get('min_num', 0 if hasattr(ElonForm.Meta.model._meta.get_field('rasmlar').field.remote_field, 'limit_choices_to') and ElonForm.Meta.model._meta.get_field('rasmlar').field.remote_field.limit_choices_to else 0): # Bu qatorni olib tashladim, chunki RasmFormda min_num yo'q
                        # Agar tasdiqlangan bo'lsa va minimal rasm soni talab qilinsa, o'shancha rasm qo'shamiz
                        # Bu joyni soddalashtirish kerak, hozircha min_num ni ElonForm da emas, viewda tekshiramiz
                        num_rasmlar = max(num_rasmlar, 3) # Masalan, tasdiqlanganlarga kamida 3 ta rasm

                    for _ in range(num_rasmlar):
                        self.create_dummy_image(elon)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"E'lon '{elon_nomi}' yaratishda xato: {e}"))

        self.stdout.write(self.style.SUCCESS(f'{elon_count} ta e\'lon muvaffaqiyatli yaratildi.'))

def create_dummy_image(self, elon_instance):
    """Tasodifiy rasm yaratib, uni Elon obyektiga bog'laydi."""
    try:
        # Oddiy rangli rasm yaratish
        width, height = random.randint(600, 1200), random.randint(400, 900)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pil_image = PILImage.new('RGB', (width, height), color=color)
        
        # Rasmga matn qo'shish (ixtiyoriy)
        # from PIL import ImageDraw
        # draw = ImageDraw.Draw(pil_image)
        # draw.text((10, 10), f"Elon ID: {elon_instance.id}\n{fake.sentence()}", fill=(255,255,255))

        image_io = BytesIO()
        pil_image.save(image_io, format='JPEG', quality=85)
        image_io.seek(0) # Fayl boshiga qaytish

        # Fayl nomini yaratish
        # Fayl nomida o'zbekcha harflar bo'lmasligi uchun transliteratsiya qilish kerak bo'lishi mumkin
        file_name_base = fake.slug() 
        image_name = f'{file_name_base}_{random.randint(1000,9999)}.jpg'
        
        # Rasm obyektini yaratish va saqlash
        # Rasm.objects.create(elon=elon_instance, image=ContentFile(image_io.read(), name=image_name))
        
        # Yoki to'g'ridan-to'g'ri Rasm modeliga save qilish:
        rasm = Rasm(elon=elon_instance)
        rasm.image.save(image_name, ContentFile(image_io.read()), save=True)

    except ImportError:
        self.stdout.write(self.style.WARNING("Pillow o'rnatilmagan. Rasmlar yaratilmadi. `pip install Pillow`"))
    except Exception as e:
        self.stdout.write(self.style.ERROR(f"Rasm yaratishda xato (Elon ID: {elon_instance.id}): {e}"))