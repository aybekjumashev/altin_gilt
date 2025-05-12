# AltinGiltApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse # Oddiy matn qaytarish uchun (kam ishlatiladi)
from .models import Elon, Rasm, Shahar, Tur
from django.contrib.auth.decorators import login_required # Faqat kirgan foydalanuvchilar uchun cheklov
from django.contrib.auth import login, authenticate, logout # Kirish/chiqish funksiyalari
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm # Standart kirish va ro'yxatdan o'tish formalari
from django.contrib import messages # Xabarlarni ko'rsatish uchun (Flask'dagi flash)
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ElonForm, RasmForm # Yangi formalarni import qilamiz
from django.forms import modelformset_factory, inlineformset_factory  # Bir nechta rasm yuklash uchun
from django.db import transaction # Bir nechta DB operatsiyalarini atomik qilish uchun
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model


CustomUser = get_user_model() # CustomUser modelini olish




def bosh_sahifa(request):
    elonlar = Elon.objects.filter(status=Elon.StatusChoices.APPROVED).order_by('-created_at')[:3]
    shaharlar = Shahar.objects.all() # Qidiruv formasi uchun
    turlar = Tur.objects.all()       # Qidiruv formasi uchun
    context = {
        'elonlar': elonlar,
        'shaharlar': shaharlar,
        'turlar': turlar,
    }
    return render(request, 'altingiltapp/index.html', context)


def elonlar_sahifasi(request):
    elonlar_list = Elon.objects.select_related('joylashuvi', 'turi', 'user').filter(status=Elon.StatusChoices.APPROVED).order_by('-created_at')
    
    # Filtrlash uchun ma'lumotlar
    shaharlar = Shahar.objects.all()
    turlar = Tur.objects.all()

    # GET parametrlari (endi ID bo'yicha bo'lishi mumkin, yoki nomi bo'yicha - hozircha nomi deb faraz qilamiz)
    shahar_filter_nomi = request.GET.get('shahar_nomi') # Yoki shahar_id
    tur_filter_nomi = request.GET.get('tur_nomi')       # Yoki tur_id

    if shahar_filter_nomi:
        elonlar_list = elonlar_list.filter(joylashuvi__nomi__iexact=shahar_filter_nomi) # __iexact nomi bo'yicha
        # Yoki agar ID bo'lsa: elonlar_list = elonlar_list.filter(joylashuvi_id=shahar_id_filter)
    if tur_filter_nomi:
        elonlar_list = elonlar_list.filter(turi__nomi__iexact=tur_filter_nomi)
        # Yoki agar ID bo'lsa: elonlar_list = elonlar_list.filter(tur_id=tur_id_filter)

    paginator = Paginator(elonlar_list, 9)
    page_number = request.GET.get('page')
    try:
        elonlar = paginator.page(page_number)
    except PageNotAnInteger:
        elonlar = paginator.page(1)
    except EmptyPage:
        elonlar = paginator.page(paginator.num_pages)

    context = {
        'elonlar': elonlar,
        'is_paginated': True,
        'page_obj': elonlar,
        'shaharlar': shaharlar, # Filtr uchun
        'turlar': turlar,       # Filtr uchun
        'selected_shahar_nomi': shahar_filter_nomi, # Tanlangan filtrni ko'rsatish uchun
        'selected_tur_nomi': tur_filter_nomi,       # Tanlangan filtrni ko'rsatish uchun
        'ElonStatusChoices': Elon.StatusChoices 
    }
    return render(request, 'altingiltapp/elonlar.html', context)


# Alohida e'lon sahifasi
def elon_sahifasi(request, elon_id):
    elon = get_object_or_404(Elon.objects.select_related('joylashuvi', 'turi', 'user'), pk=elon_id)
    if not (elon.status == Elon.StatusChoices.APPROVED or (request.user.is_authenticated and elon.user == request.user)):
        from django.http import Http404
        raise Http404("E'lon topilmadi yoki ko'rishga ruxsat yo'q.")
    context = {'elon': elon}
    return render(request, 'altingiltapp/elon.html', context)





# E'lon qo'shish
@login_required
def elon_qoshish(request): 
    RasmInlineFormSet = inlineformset_factory(
        Elon, Rasm, form=RasmForm,
        extra=5, max_num=10, min_num=3,
        validate_min=True, can_delete=False
    )

    if request.method == 'POST':
        elon_form = ElonForm(request.POST)
        formset = RasmInlineFormSet(request.POST, request.FILES, prefix='rasmlar_yangi')

        if elon_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    new_elon = elon_form.save(commit=False)
                    new_elon.user = request.user
                    new_elon.status = Elon.StatusChoices.PENDING # Avtomatik moderatsiyaga
                    new_elon.moderation_notes = None # Eski izohlarni tozalash (tahrir uchun kerak bo'ladi)
                    new_elon.save()

                    formset.instance = new_elon
                    formset.save()
                messages.success(request, "E'lon moderatsiyaga muvaffaqiyatli yuborildi!")
                return redirect('AltinGiltApp:shaxsiy_kabinet') # Kabinetga yo'naltirish yaxshiroq
            except Exception as e:
                messages.error(request, f"E'lonni saqlashda xatolik yuz berdi: {e}")
        else:
            messages.error(request, "Iltimos, formadagi xatoliklarni to'g'rilang.")
    else:
        elon_form = ElonForm()
        formset = RasmInlineFormSet(prefix='rasmlar_yangi')

    context = {
        'elon_form': elon_form,
        'formset': formset,
        'form_title': "Yangi E'lon Joylashtirish",
        'submit_button_text': "Moderatsiyaga Yuborish"
    }
    return render(request, 'altingiltapp/elon_qoshish.html', context)

@login_required
def elon_tahrirlash(request, elon_id):
    elon = get_object_or_404(Elon, pk=elon_id, user=request.user)

    RasmInlineFormSet = inlineformset_factory(
        Elon, Rasm, form=RasmForm,
        fields=['image'], # Faqat 'image' maydonini ishlatamiz RasmFormda
        extra=3,
        min_num=0, # Tahrirda minimal shart emas
        validate_min=False,
        can_delete=True
    )

    if request.method == 'POST':
        elon_form = ElonForm(request.POST, request.FILES, instance=elon) # ElonForm'ga ham FILES kerak (agar unda FileField bo'lsa)
        formset = RasmInlineFormSet(request.POST, request.FILES, instance=elon, prefix='rasmlar') # prefix qo'shib ko'ramiz

        print(f"--- POST DATA ---")
        print(request.POST)
        print(f"--- FILES DATA ---")
        print(request.FILES)
        print(f"Elon form valid: {elon_form.is_valid()}")
        if not elon_form.is_valid():
            print(f"Elon form errors: {elon_form.errors.as_json()}")
        
        print(f"Formset valid: {formset.is_valid()}")
        if not formset.is_valid():
            print(f"Formset errors: {formset.errors}") # To'liq error arrayini ko'rish
            print(f"Formset non_form_errors: {formset.non_form_errors()}")
            for i, form_in_fs in enumerate(formset.forms):
                 print(f"Formset form #{i} initial: {form_in_fs.initial}")
                 print(f"Formset form #{i} instance: {form_in_fs.instance}, instance.pk: {form_in_fs.instance.pk if form_in_fs.instance else None}")
                 print(f"Formset form #{i} changed_data: {form_in_fs.changed_data}")
                 print(f"Formset form #{i} errors: {form_in_fs.errors.as_json()}")


        if elon_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    edited_elon = elon_form.save(commit=False)
                    edited_elon.status = Elon.StatusChoices.PENDING # Model nomini to'g'ri yozing
                    edited_elon.moderation_notes = None
                    edited_elon.save()
                    elon_form.save_m2m() # Agar ElonFormda m2m bo'lsa

                    # Formsetni saqlashdan oldin yana bir tekshiruv
                    for form_in_fs in formset:
                        print(f"Saving form for instance: {form_in_fs.instance}, pk: {form_in_fs.instance.pk if form_in_fs.instance else 'None'}")
                        if form_in_fs.cleaned_data.get('DELETE') and form_in_fs.instance.pk:
                            print(f"Deleting instance {form_in_fs.instance.pk}")
                        elif form_in_fs.has_changed() or not form_in_fs.instance.pk : # Yoki yangi, yoki o'zgargan
                             if form_in_fs.cleaned_data.get('image') or not form_in_fs.instance.pk: # Agar rasm kelgan bo'lsa yoki yangi bo'lsa
                                print(f"Saving instance {form_in_fs.instance.pk if form_in_fs.instance.pk else 'NEW'} with image {form_in_fs.cleaned_data.get('image')}")
                        # else:
                            # print(f"Skipping save for instance {form_in_fs.instance.pk} - no changes or no new image")

                    formset.save()

                messages.success(request, "E'lon muvaffaqiyatli tahrirlandi va qayta moderatsiyaga yuborildi.")
                return redirect('AltinGiltApp:shaxsiy_kabinet')
            except Exception as e:
                messages.error(request, f"E'lonni tahrirlashda xatolik yuz berdi: {e}")
        else:
            # Xatoliklarni yig'ish qismi avvalgidek qoladi
            error_list = []
            if elon_form.errors:
                error_list.append(f"E'lon formasi xatolari: {elon_form.errors.as_ul()}")
            if any(formset.errors): # Check if there are any errors in the formset
                for i, errors_dict in enumerate(formset.errors):
                    if errors_dict:
                        ul_errors = "<ul>"
                        for field, errors in errors_dict.items():
                            ul_errors += f"<li>{field}: {', '.join(errors)}</li>"
                        ul_errors += "</ul>"
                        error_list.append(f"Rasm #{i+1} xatolari: {ul_errors}")
            if formset.non_form_errors():
                 error_list.append(f"Umumiy rasm xatolari: {formset.non_form_errors().as_ul()}")
            
            messages.error(request, "Iltimos, formadagi xatoliklarni to'g'rilang:<br>" + "<br>".join(error_list), extra_tags='safe')


    else: # GET request
        elon_form = ElonForm(instance=elon)
        formset = RasmInlineFormSet(instance=elon, prefix='rasmlar') # GET uchun ham prefix

    context = {
        'elon_form': elon_form,
        'formset': formset,
        'elon': elon,
        'form_title': f"'{elon.nomi}' e'lonini tahrirlash",
        'submit_button_text': "O'zgarishlarni Saqlash"
    }
    return render(request, 'altingiltapp/elon_qoshish.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('AltinGiltApp:bosh_sahifa') # Agar kirgan bo'lsa, bosh sahifaga

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Ro'yxatdan o'tish muvaffaqiyatli!")
            return redirect('AltinGiltApp:bosh_sahifa')
        else:
            # Xatoliklarni chiroyliroq chiqarish
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__': # Umumiy xatolar uchun
                         messages.error(request, error)
                    else:
                        messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = CustomUserCreationForm()
    context = {'form': form, 'title': "Ro'yxatdan o'tish"}
    return render(request, 'registration/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('AltinGiltApp:bosh_sahifa')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST) # `request` ni birinchi argument sifatida berish muhim
        if form.is_valid():
            phone_number = form.cleaned_data.get('username') # Formada 'username' deb nomlangan (labeli 'Telefon raqami')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=phone_number, password=password) # `username` parametri `USERNAME_FIELD` ga mos kelishi kerak
            
            if user is not None:
                login(request, user)
                messages.info(request, f"Xush kelibsiz, {user.first_name}!")
                next_page = request.POST.get('next') or request.GET.get('next')
                if not next_page or next_page == 'None' or not next_page.startswith('/'):
                     next_page = 'AltinGiltApp:bosh_sahifa' 
                return redirect(next_page)
            else:
                messages.error(request, "Telefon raqami yoki parol noto'g'ri.")
        else:
             # Xatoliklarni chiroyliroq chiqarish
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                         messages.error(request, error)
                    # else: # Maydon nomi bilan xato chiqarish shart emas, forma o'zi ko'rsatadi
                         # messages.error(request, f"{form.fields[field].label}: {error}") 
            if not form.errors: # Agar maydon xatosi bo'lmasa, umumiy xato
                messages.error(request, "Telefon raqami yoki parol noto'g'ri (form xatosi).")

    else:
        form = CustomAuthenticationForm()
    
    next_param = request.GET.get('next', '')
    context = {
        'form': form, 
        'title': "Kirish",
        'next': next_param
    }
    return render(request, 'registration/login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('AltinGiltApp:bosh_sahifa') # Bosh sahifaga qaytish


# Shaxsiy kabinet
@login_required
def shaxsiy_kabinet(request):
    elonlar = Elon.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'elonlar': elonlar,
        'user': request.user,
        'ElonStatusChoices': Elon.StatusChoices # Statuslarni shablonda taqqoslash uchun
    }
    return render(request, 'altingiltapp/shaxsiy_kabinet.html', context)

