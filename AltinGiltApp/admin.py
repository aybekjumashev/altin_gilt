from django.contrib import admin
from .models import Elon, Rasm # Joriy papkadagi ('.') models faylidan Elon va Rasm ni import qilamiz

# Eng oddiy ro'yxatdan o'tkazish usuli
admin.site.register(Elon)
admin.site.register(Rasm)

# --- Keyinchalik admin panelini moslashtirishimiz mumkin ---
# Masalan, Elon uchun qo'shimcha sozlamalar bilan:
# @admin.register(Elon)
# class ElonAdmin(admin.ModelAdmin):
#     list_display = ('nomi', 'joylashuvi', 'turi', 'narxi', 'user', 'created_at') # Ro'yxatda ko'rinadigan ustunlar
#     list_filter = ('turi', 'joylashuvi', 'created_at') # Filtrlash uchun maydonlar
#     search_fields = ('nomi', 'batafsil', 'joylashuvi') # Qidirish uchun maydonlar
#     date_hierarchy = 'created_at' # Sana bo'yicha iyerarxiya

# Rasm uchun ham xuddi shunday qilsa bo'ladi
# @admin.register(Rasm)
# class RasmAdmin(admin.ModelAdmin):
#     list_display = ('id', 'elon', 'image') # Ro'yxatda ko'rinadigan ustunlar
#     list_filter = ('elon',) # E'lon bo'yicha filtrlash
#     # ImageField uchun rasm preview ko'rsatish mumkin (murakkabroq)