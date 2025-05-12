# AltinGiltApp/urls.py
from django.urls import path
from . import views # Joriy papkadagi views faylini import qilamiz

# Bu katta loyihalarda nomlar to'qnashuvining oldini oladi
app_name = 'AltinGiltApp' 

urlpatterns = [
    path('', views.bosh_sahifa, name='bosh_sahifa'),
    path('elonlar/', views.elonlar_sahifasi, name='elonlar_list'),
    path('elonlar/<int:elon_id>/', views.elon_sahifasi, name='elon_detail'),
    path('elon_qoshish/', views.elon_qoshish, name='elon_create'),
    path('elon_tahrirlash/<int:elon_id>/', views.elon_tahrirlash, name='elon_edit'),
    path('elon_ochirish/<int:elon_id>/', views.elon_ochirish, name='elon_delete'), 
    path('register/', views.register_view, name='register'), 
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'), 
    path('kabinet/', views.shaxsiy_kabinet, name='shaxsiy_kabinet'),
    path('kabinet/tahrirlash/', views.profile_edit_view, name='profile_edit'),
]