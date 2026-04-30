from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'uauth'

urlpatterns = [
    # login 1) login page   2) login function
    path('login/', auth_views.LoginView.as_view(template_name='uauth/login.html'),name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('check_username/', views.check_username, name='check_username'),
    path('password/change/', views.password_change, name='password_change'),
    path('withdraw/verify/', views.withdraw_verify, name='withdraw_verify'),
    path('withdraw/confirm/', views.withdraw_confirm, name='withdraw_confirm'),
]
