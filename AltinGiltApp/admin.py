from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Asos UserAdmin
from .models import CustomUser, Elon, Rasm, Shahar, Tur
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html 

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    # UserAdmin dagi fieldsetlarni moslashtirish
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Shaxsiy ma\'lumotlar'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Ruxsatlar'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        # (_('Muhim sanalar'), {'fields': ('last_login', 'date_joined')}), # <<< BU QATORNI KOMMENTGA OLAMIZ YOKI O'CHIRAMIZ
    )
    # Yoki, agar bu fieldset qolishini xohlasangiz, 'last_login' va 'date_joined' ni readonly_fields ga qo'shing

    # Ro'yxatda ko'rinadigan maydonlar
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login') # Ro'yxatga qo'shish mumkin
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    ordering = ('phone_number',)

    # Faqat o'qish uchun mo'ljallangan maydonlar
    readonly_fields = ('last_login', 'date_joined') # <<<--- BU QATORNI QO'SHING YOKI YANGILANG

    # Yangi foydalanuvchi qo'shish formasi uchun maydonlar (add_fieldsets)
    # BaseUserAdmin'ning standart add_formiga tayansak, bu qism shart emas,
    # lekin agar maxsus forma bo'lsa, uni moslashtirish kerak.
    # Hozircha BaseUserAdmin'dagi add_fieldsets'dan foydalanamiz.
    # Agar add_fieldsets'ni o'zingiz belgilamoqchi bo'lsangiz:
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # 'password2' standart UserCreationForm'dan, bizning formamizda yo'q bo'lishi mumkin
            'fields': ('phone_number', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )
    # add_form da ham `date_joined` bo'lmasligi kerak.

# Eski admin.site.unregister(User) kerak emas, chunki biz yangi modelni ro'yxatdan o'tkazamiz
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Shahar)
class ShaharAdmin(admin.ModelAdmin):
    list_display = ('nomi',)
    search_fields = ('nomi',)
    # prepopulated_fields = {'slug': ('nomi',)} # Agar slug maydoni bo'lsa

@admin.register(Tur)
class TurAdmin(admin.ModelAdmin):
    list_display = ('nomi',)
    search_fields = ('nomi',)
    # prepopulated_fields = {'slug': ('nomi',)} # Agar slug maydoni bo'lsa


class RasmInline(admin.TabularInline): # Yoki admin.StackedInline
    model = Rasm
    extra = 1 # Yangi rasm qo'shish uchun nechta bo'sh joy (tahrirda)
    readonly_fields = ('image_preview',) # Rasm previewini ko'rsatish uchun

    def image_preview(self, obj):
        # obj bu yerda Rasm instance
        if obj.image:
            return format_html('<a href="{}"><img src="{}" width="150" height="auto" /></a>', obj.image.url, obj.image.url)
        return _("(Rasm yo'q)")
    image_preview.short_description = _('Rasm Ko\'rinishi')


# ElonAdmin o'zgarishsiz qolishi mumkin, faqat 'user__username' o'rniga 'user__phone_number' ishlatiladi
@admin.register(Elon)
class ElonAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'user', 'status', 'joylashuvi', 'manzil', 'turi', 'narxi', 'created_at')
    list_filter = ('status', 'turi', 'joylashuvi', 'created_at')
    search_fields = ('nomi', 'manzil', 'batafsil', 'joylashuvi__nomi', 'turi__nomi', 'user__phone_number', 'user__first_name') # O'zgartirildi
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    autocomplete_fields = ['joylashuvi', 'turi', 'user']

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            'fields': ('nomi', 'user', 'joylashuvi', 'manzil', 'turi', 'narxi', 'batafsil')
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
    inlines = [RasmInline]
    
    @admin.action(description="Tanlangan e'lonlarni tasdiqlash")
    def make_approved(self, request, queryset):
        queryset.update(status=Elon.StatusChoices.APPROVED, moderation_notes=None)
        self.message_user(request, f"{queryset.count()} ta e'lon muvaffaqiyatli tasdiqlandi.")

    actions = [make_approved]

    def save_model(self, request, obj, form, change):
        # if not obj.user_id and hasattr(request, 'user') and request.user.is_authenticated:
        # obj.user = request.user # Bu qatorni olib tashladim, chunki user tanlanishi kerak
        if 'status' in form.changed_data and obj.status == Elon.StatusChoices.APPROVED:
            obj.moderation_notes = None
        elif 'status' in form.changed_data and obj.status == Elon.StatusChoices.REJECTED and not obj.moderation_notes:
            from django.contrib import messages
            messages.warning(request, "E'lon rad etildi, lekin sababi ko'rsatilmadi. Iltimos, izoh qoldiring.")
        super().save_model(request, obj, form, change)

# admin.site.register(Rasm)