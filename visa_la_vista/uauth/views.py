from django.shortcuts import render, redirect
import django.contrib.auth as auth
from .models import UserForm, UserDetail
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

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


def _account_context(request, **extra):
    display_user = request.user if request.user.is_authenticated else None
    context = {
        'account_name': getattr(display_user, 'username', 'hello'),
        'account_email': getattr(display_user, 'email', 'auser@example.com') or 'auser@example.com',
    }
    context.update(extra)
    return context


def password_change(request):
    errors = {}

    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        new_password_confirm = request.POST.get('new_password_confirm', '')

        if request.user.is_authenticated and not request.user.check_password(current_password):
            errors['current_password'] = '비밀번호가 일치하지 않습니다.'

        if new_password != new_password_confirm:
            errors['new_password_confirm'] = '비밀번호가 일치하지 않습니다.'

        try:
            if request.user.is_authenticated:
                validate_password(new_password, request.user)
        except ValidationError:
            errors['new_password'] = '비밀번호 형식을 다시 확인해주세요.'

        if request.user.is_authenticated and not errors:
            request.user.set_password(new_password)
            request.user.save(update_fields=['password'])
            update_session_auth_hash(request, request.user)
            return redirect('index')

    return render(
        request,
        'uauth/password_change.html',
        _account_context(request, errors=errors),
    )


def withdraw_verify(request):
    errors = {}

    if request.method == 'POST':
        password = request.POST.get('password', '')

        if request.user.is_authenticated and request.user.check_password(password):
            request.session['withdraw_verified'] = True
            return redirect('uauth:withdraw_confirm')

        errors['password'] = '비밀번호가 일치하지 않습니다.'

    return render(
        request,
        'uauth/withdraw_verify.html',
        _account_context(request, errors=errors),
    )


def withdraw_confirm(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            auth.logout(request)
            user.delete()
        return redirect('index')

    return render(
        request,
        'uauth/withdraw_confirm.html',
        _account_context(request),
    )
