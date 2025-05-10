# AltinGilt/urls.py
from django.contrib import admin
from django.urls import path, include # include ni import qilinganiga ishonch hosil qiling
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # '/' bilan boshlangan barcha so'rovlarni AltinGiltApp/urls.py fayliga yo'naltirish
    path('', include('AltinGiltApp.urls')), # Avvalgi kommentariyani olib tashlang va yo'lni to'g'rilang
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Agar django-debug-toolbar o'rnatilgan bo'lsa, uni ham shu yerga qo'shish mumkin
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns