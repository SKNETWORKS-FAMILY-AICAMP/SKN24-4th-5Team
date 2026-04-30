from django.shortcuts import render, redirect
import django.contrib.auth as auth
from .models import UserForm, UserDetail
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Create your views here.
def login(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        next_url = request.POST.get('next') or '/'

        if not username or not password:
            return JsonResponse(
                {'success': False, 'message': '이메일과 비밀번호를 입력해주세요.'},
                status=400,
            )

        user = auth.authenticate(request, username=username, password=password)

        if user is None:
            return JsonResponse(
                {'success': False, 'message': '이메일 또는 비밀번호가 일치하지 않습니다.'},
                status=400,
            )

        auth.login(request, user)
        return JsonResponse({'success': True, 'redirect_url': next_url})

    return render(request, 'uauth/login.html')

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

def check_email(request):
    email = (request.GET.get('email') or '').strip()

    if not email:
        return JsonResponse({'available': False, 'message': '이메일을 입력해주세요.'})

    is_exists = User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists()

    if is_exists:
        return JsonResponse({'available': False, 'message': '이미 사용중인 이메일입니다.'})
    return JsonResponse({'available': True, 'message': '사용 가능한 이메일입니다.'})

def password_reset_update(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=405)

    email = (request.POST.get('email') or '').strip()
    new_password = request.POST.get('new_password') or ''
    new_password_confirm = request.POST.get('new_password_confirm') or ''
    user = User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).first()

    if not user:
        return JsonResponse({'success': False, 'message': '등록되어있지 않은 이메일입니다.'}, status=400)

    if new_password != new_password_confirm:
        return JsonResponse({'success': False, 'message': '비밀번호가 일치하지 않습니다.'}, status=400)

    try:
        validate_password(new_password, user)
    except ValidationError:
        return JsonResponse({'success': False, 'message': '비밀번호 형식을 다시 확인해주세요.'}, status=400)

    user.set_password(new_password)
    user.save()
    return JsonResponse({'success': True, 'message': '비밀번호가 재설정되었습니다.'})


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
        wants_json = 'application/json' in request.headers.get('Accept', '')

        if request.user.is_authenticated and request.user.check_password(password):
            request.session['withdraw_verified'] = True
            if wants_json:
                return JsonResponse({'success': True})
            return redirect('uauth:withdraw_confirm')

        errors['password'] = '비밀번호가 일치하지 않습니다.'
        request.session.pop('withdraw_verified', None)
        if wants_json:
            return JsonResponse({'success': False, 'message': errors['password']}, status=400)
    else:
        request.session.pop('withdraw_verified', None)

    return render(
        request,
        'uauth/withdraw_verify.html',
        _account_context(request, errors=errors),
    )


def withdraw_confirm(request):
    if not request.session.get('withdraw_verified'):
        return redirect('uauth:withdraw_verify')

    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            auth.logout(request)
            user.delete()
            request.session.pop('withdraw_verified', None)
        return redirect('index')

    return render(
        request,
        'uauth/withdraw_confirm.html',
        _account_context(request),
    )
