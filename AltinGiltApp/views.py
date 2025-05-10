# AltinGiltApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse # Oddiy matn qaytarish uchun (kam ishlatiladi)
from .models import Elon, Rasm # Modellarimizni import qilamiz
from django.contrib.auth.decorators import login_required # Faqat kirgan foydalanuvchilar uchun cheklov
from django.contrib.auth import login, authenticate, logout # Kirish/chiqish funksiyalari
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm # Standart kirish va ro'yxatdan o'tish formalari
from django.contrib import messages # Xabarlarni ko'rsatish uchun (Flask'dagi flash)
from .forms import ElonForm, RasmForm # Keyinroq yaratadigan formalarimiz
from django.forms import modelformset_factory, inlineformset_factory  # Bir nechta rasm yuklash uchun
from django.db import transaction # Bir nechta DB operatsiyalarini atomik qilish uchun
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def bosh_sahifa(request):
    # Oxirgi 3 ta e'lonni olish (yoki boshqa mezon bo'yicha)
    elonlar = Elon.objects.order_by('-created_at')[:3]
    context = {
        'elonlar': elonlar,
    }
    # Shablonni render qilish va javob qaytarish
    return render(request, 'altingiltapp/index.html', context)

def elonlar_sahifasi(request):
    elonlar_list = Elon.objects.order_by('-created_at')
    shahar = request.GET.get('shahar')
    tur = request.GET.get('tur')

    if shahar:
        elonlar_list = elonlar_list.filter(joylashuvi__icontains=shahar)
    if tur:
        elonlar_list = elonlar_list.filter(turi=tur)

    # Pagination logikasi
    paginator = Paginator(elonlar_list, 9) # Har sahifada 9 ta e'lon
    page_number = request.GET.get('page')
    try:
        elonlar = paginator.page(page_number)
    except PageNotAnInteger:
        # Agar page parametri son bo'lmasa, birinchi sahifani ko'rsatish
        elonlar = paginator.page(1)
    except EmptyPage:
        # Agar page raqami diapazondan tashqarida bo'lsa, oxirgi sahifani ko'rsatish
        elonlar = paginator.page(paginator.num_pages)

    context = {
        'elonlar': elonlar, # Endi bu page obyekti
        'is_paginated': True, # Shablon uchun flag
        'page_obj': elonlar, # Shablon standart nomni ishlatishi uchun
        'selected_shahar': shahar,
        'selected_tur': tur,
    }
    return render(request, 'altingiltapp/elonlar.html', context)

def elon_sahifasi(request, elon_id):
    # E'lonni ID bo'yicha topish, topilmasa 404 xato qaytarish
    elon = get_object_or_404(Elon, pk=elon_id) # pk - primary key (id)
    context = {
        'elon': elon,
    }
    return render(request, 'altingiltapp/elon.html', context)



@login_required
def elon_qoshish(request):
    # Inline Formset: Elon va unga bog'liq Rasmlar uchun juda qulay
    # extra=5: Standart 5 ta bo'sh rasm formasi chiqaradi
    # max_num=10: Maksimal 10 ta rasm yuklash mumkin
    # min_num=3: Kamida 3 ta rasm yuklanishini talab qiladi (agar kerak bo'lsa)
    # can_delete=False: Yangi e'lon qo'shishda o'chirish checkboxi kerak emas
    RasmInlineFormSet = inlineformset_factory(
        Elon, Rasm, form=RasmForm,
        extra=5, max_num=10, min_num=3, # Kamida 3 ta rasm talabini qo'shdik
        validate_min=True, # min_num ni tekshirishni aktivlashtiradi
        can_delete=False
    )

    if request.method == 'POST':
        # Elon formasini POST ma'lumotlari bilan to'ldirish
        elon_form = ElonForm(request.POST)
        # Formsetni POST ma'lumotlari va yuklangan fayllar bilan to'ldirish
        # instance=Elon() kerak emas, chunki hali saqlanmagan
        formset = RasmInlineFormSet(request.POST, request.FILES)

        # Elon formasi va Formset valid (to'g'ri) ekanligini tekshirish
        if elon_form.is_valid() and formset.is_valid():
            try:
                # Atomik tranzaksiya: Elon yoki Rasm saqlashda xatolik bo'lsa, hammasi bekor qilinadi
                with transaction.atomic():
                    # 1. Elonni saqlash (lekin hali commit qilmaslik)
                    #    Foydalanuvchini avtomatik bog'lash
                    new_elon = elon_form.save(commit=False)
                    new_elon.user = request.user
                    new_elon.save() # Endi Elon bazaga saqlanadi va ID oladi

                    # 2. Formsetni saqlash
                    #    instance=new_elon: har bir Rasm obyektini shu yangi e'longa bog'laydi
                    formset.instance = new_elon
                    formset.save()

                messages.success(request, "E'lon va rasmlar muvaffaqiyatli qo'shildi!")
                # Foydalanuvchini yangi qo'shilgan e'lon sahifasiga yo'naltirish
                return redirect('AltinGiltApp:elon_detail', elon_id=new_elon.id)

            except Exception as e:
                # Agar tranzaksiya ichida xatolik bo'lsa
                messages.error(request, f"E'lonni saqlashda xatolik yuz berdi: {e}")
                # Formani va formsetni xatolar bilan qayta ko'rsatish uchun pastga tushamiz

        else: # Agar form yoki formset valid bo'lmasa
            # Xatoliklarni ko'rsatish uchun xabar (ixtiyoriy, chunki forma o'zi xatolarni ko'rsatadi)
            messages.error(request, "Iltimos, formadagi xatoliklarni to'g'rilang.")
            # Shablon xatoliklarni form/formset orqali ko'rsatadi

    else: # GET request (sahifa birinchi marta ochilganda)
        elon_form = ElonForm()
        # Bo'sh formset yaratish (instance ko'rsatilmaydi)
        formset = RasmInlineFormSet()

    context = {
        'elon_form': elon_form,
        'formset': formset,
    }
    return render(request, 'altingiltapp/elon_qoshish.html', context)


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Ro'yxatdan o'tgandan so'ng avtomatik kirish
            messages.success(request, "Ro'yxatdan o'tish muvaffaqiyatli!")
            return redirect('AltinGiltApp:bosh_sahifa') # Yoki boshqa sahifaga
        else:
            # Formada xatoliklar bo'lsa, xabarlarni ko'rsatish
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            # Yoki shunchaki umumiy xabar
            # messages.error(request, "Formani to'ldirishda xatoliklar mavjud.")
    else: # GET request
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context) # Shablon joylashuvini o'zgartirdik

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Xush kelibsiz, {username}!")
                # Keyingi sahifaga yo'naltirish (agar 'next' parametri bo'lsa)
                next_page = request.POST.get('next', '/') # Yoki request.GET.get(...)
                if not next_page or next_page == 'None': # Ba'zan 'None' string kelishi mumkin
                     next_page = '/' 
                return redirect(next_page)
            else:
                messages.error(request, "Login yoki parol noto'g'ri.")
        else:
            messages.error(request, "Login yoki parol noto'g'ri.")
    else: # GET request
        form = AuthenticationForm()
        # 'next' parametrini shablonga uzatish
        next_page = request.GET.get('next', '/')
    context = {
        'form': form,
        'next': next_page # Shablon form action'iga qo'shish uchun
    }
    return render(request, 'registration/login.html', context) # Shablon joylashuvi

def logout_view(request):
    logout(request)
    messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('AltinGiltApp:bosh_sahifa') # Bosh sahifaga qaytish

@login_required
def shaxsiy_kabinet(request):
    # Joriy foydalanuvchining e'lonlarini olish
    elonlar = Elon.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'elonlar': elonlar,
        # request.user shablonda avtomatik mavjud bo'ladi, lekin aniqlik uchun qo'shish mumkin
        'user': request.user
    }
    return render(request, 'altingiltapp/shaxsiy_kabinet.html', context)

