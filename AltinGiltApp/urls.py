# AltinGiltApp/urls.py
from django.urls import path
from . import views # Joriy papkadagi views faylini import qilamiz

# Bu katta loyihalarda nomlar to'qnashuvining oldini oladi
app_name = 'AltinGiltApp' 

urlpatterns = [
    # Bosh sahifa (masalan, http://127.0.0.1:8000/)
    path('', views.bosh_sahifa, name='bosh_sahifa'),
    # Barcha e'lonlar sahifasi (masalan, http://127.0.0.1:8000/elonlar/)
    path('elonlar/', views.elonlar_sahifasi, name='elonlar_list'),
    # Alohida e'lon sahifasi (masalan, http://127.0.0.1:8000/elonlar/5/)
    # <int:elon_id> - URL'dan butun son (integer) parametrini oladi va uni 'elon_id' nomi bilan view funksiyasiga uzatadi
    path('elonlar/<int:elon_id>/', views.elon_sahifasi, name='elon_detail'),
    # Yangi e'lon qo'shish sahifasi (masalan, http://127.0.0.1:8000/elon_qoshish/)
    path('elon_qoshish/', views.elon_qoshish, name='elon_create'),
    # Ro'yxatdan o'tish sahifasi (masalan, http://127.0.0.1:8000/register/)
    path('register/', views.register_view, name='register'), # view nomini 'register' dan o'zgartirdik, Django o'zida shunday nom bor
    # Kirish sahifasi (masalan, http://127.0.0.1:8000/login/)
    path('login/', views.login_view, name='login'), # view nomini moslashtirdik
     # Chiqish (masalan, http://127.0.0.1:8000/logout/)
    path('logout/', views.logout_view, name='logout'), # view nomini moslashtirdik
    # Shaxsiy kabinet (masalan, http://127.0.0.1:8000/kabinet/)
    path('kabinet/', views.shaxsiy_kabinet, name='shaxsiy_kabinet'),
]