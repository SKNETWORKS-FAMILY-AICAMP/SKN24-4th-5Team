from django.shortcuts import render, redirect
import django.contrib.auth as auth
from .models import UserForm, UserDetail
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import transaction

# Create your views here.
def logout(request):
    auth.logout(request)
    return redirect('/')

# @transaction.atomic
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=True)
                user_detail = UserDetail(
                    user=user,
                    birthday=form.cleaned_data.get('birthday'),
                    profile=form.cleaned_data.get('profile')
                )
                user_detail.save()
                print(f' ----------- 회원가입 완료: {user_detail} -----------')

                # 회원가입후 자동 로그인 (auto login after signup) 
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = auth.authenticate(username=username, password=raw_password)
                auth.login(request, user)
                return redirect('index')

    else:   # request.method == 'GET':
        form = UserForm()
    
    return render(request, 'uauth/signup.html', {'form': form})

def check_username(request):
    username = request.GET.get('username')
    is_exists = User.objects.filter(username=username)

    if is_exists:
        return JsonResponse({'available': False, 'message':'이미 사용중인 ID입니다.'})
    return JsonResponse({'available': True, 'message':'사용 가능한 ID입니다.'})
        