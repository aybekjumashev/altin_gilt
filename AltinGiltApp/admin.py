from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Asos UserAdmin
from .models import CustomUser, Elon, Rasm
from django.utils.translation import gettext_lazy as _

# CustomUserAdmin
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    # UserAdmin dagi fieldsetlarni moslashtirish
    # Asosiy ma'lumotlar
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Shaxsiy ma\'lumotlar'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Ruxsatlar'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Muhim sanalar'), {'fields': ('last_login', 'date_joined')}),
    )
    # Ro'yxatda ko'rinadigan maydonlar
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    # Qidiruv maydonlari
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    # Tartiblash
    ordering = ('phone_number',)
    # Yangi foydalanuvchi qo'shish formasi uchun maydonlar
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'email', 'password', 'password2', 
                       'is_staff', 'is_superuser', 'groups', 'user_permissions'), # password2 UserCreationForm dan keladi
        }),
    )
    # Agar UserCreationForm'ni admin uchun ham moslashtirsangiz, 'password2' ni formdan olish kerak
    # Hozircha BaseUserAdmin'ning standart add_form'iga tayanamiz.
    # add_form = CustomUserCreationForm # Agar admin uchun maxsus yaratish formasi bo'lsa

# Eski admin.site.unregister(User) kerak emas, chunki biz yangi modelni ro'yxatdan o'tkazamiz
admin.site.register(CustomUser, CustomUserAdmin)


# ElonAdmin o'zgarishsiz qolishi mumkin, faqat 'user__username' o'rniga 'user__phone_number' ishlatiladi
@admin.register(Elon)
class ElonAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'user', 'status', 'joylashuvi', 'turi', 'narxi', 'created_at', 'updated_at')
    list_filter = ('status', 'turi', 'joylashuvi', 'created_at')
    search_fields = ('nomi', 'batafsil', 'joylashuvi', 'user__phone_number', 'user__first_name') # O'zgartirildi
    date_hierarchy = 'created_at'
    list_editable = ('status',)

    fieldsets = (
        (None, {
            'fields': ('nomi', 'user', 'joylashuvi', 'turi', 'narxi', 'batafsil')
        }),
        ('Moderatsiya', {
            'fields': ('status', 'moderation_notes'),
            'classes': ('collapse',), 
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at') # Userni endi readonly qilmaymiz, chunki CustomUser
                                                    # admin panelida tanlanishi mumkin. Yoki qoldirish mumkin.

    @admin.action(description="Tanlangan e'lonlarni tasdiqlash")
    def make_approved(self, request, queryset):
        queryset.update(status=Elon.StatusChoices.APPROVED, moderation_notes=None)
        self.message_user(request, f"{queryset.count()} ta e'lon muvaffaqiyatli tasdiqlandi.")

    actions = [make_approved]

    def save_model(self, request, obj, form, change):
        if not obj.user_id: # Agar e'lon yangi qo'shilayotgan bo'lsa va admin user tanlamagan bo'lsa
            obj.user = request.user # Adminni e'lon egasi qilib belgilash (agar kerak bo'lsa)
        
        if 'status' in form.changed_data and obj.status == Elon.StatusChoices.APPROVED:
            obj.moderation_notes = None
        elif 'status' in form.changed_data and obj.status == Elon.StatusChoices.REJECTED and not obj.moderation_notes:
            from django.contrib import messages # messages ni import qilish
            messages.warning(request, "E'lon rad etildi, lekin sababi ko'rsatilmadi. Iltimos, izoh qoldiring.")
        super().save_model(request, obj, form, change)

admin.site.register(Rasm)