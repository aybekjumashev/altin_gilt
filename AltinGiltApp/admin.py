from django.contrib import admin
from .models import Elon, Rasm # Joriy papkadagi ('.') models faylidan Elon va Rasm ni import qilamiz
from django.contrib import messages # Xabarlarni ko'rsatish uchun (Flask'dagi flash)

@admin.register(Elon)
class ElonAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'user', 'status', 'joylashuvi', 'turi', 'narxi', 'created_at', 'updated_at')
    list_filter = ('status', 'turi', 'joylashuvi', 'created_at')
    search_fields = ('nomi', 'batafsil', 'joylashuvi', 'user__username')
    date_hierarchy = 'created_at'
    list_editable = ('status',) # Ro'yxatdan turib statusni o'zgartirish (ehtiyot bo'ling)

    fieldsets = (
        (None, {
            'fields': ('nomi', 'user', 'joylashuvi', 'turi', 'narxi', 'batafsil')
        }),
        ('Moderatsiya', {
            'fields': ('status', 'moderation_notes'),
            'classes': ('collapse',), # Boshida yopiq turadi
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'user') # Userni o'zgartirib bo'lmasin

    # E'lonni tasdiqlash uchun action
    @admin.action(description="Tanlangan e'lonlarni tasdiqlash")
    def make_approved(self, request, queryset):
        queryset.update(status=Elon.StatusChoices.APPROVED, moderation_notes=None) # Izohni tozalash
        self.message_user(request, f"{queryset.count()} ta e'lon muvaffaqiyatli tasdiqlandi.")

    # E'lonni rad etish uchun action (izoh bilan birga qilish qiyinroq,
    # shuning uchun hozircha faqat tasdiqlashni qo'shamiz. Rad etishni alohida edit qilib bajarish mumkin)
    # Yoki custom action view yaratish kerak bo'ladi.

    actions = [make_approved]

    # Formani saqlashdan oldin/keyin logikani qo'shish mumkin
    def save_model(self, request, obj, form, change):
        # Agar status "Tasdiqlangan" ga o'zgarsa va avval izoh bo'lgan bo'lsa, izohni tozalash
        if 'status' in form.changed_data and obj.status == Elon.StatusChoices.APPROVED:
            obj.moderation_notes = None
        # Agar status "Rad etilgan" ga o'zgarsa va izoh bo'sh bo'lsa, xabar berish (lekin formani to'xtatmaydi)
        elif 'status' in form.changed_data and obj.status == Elon.StatusChoices.REJECTED and not obj.moderation_notes:
            messages.warning(request, "E'lon rad etildi, lekin sababi ko'rsatilmadi. Iltimos, izoh qoldiring.")
        super().save_model(request, obj, form, change)


admin.site.register(Rasm) # Rasm uchun oddiy ro'yxatdan o'tkazish