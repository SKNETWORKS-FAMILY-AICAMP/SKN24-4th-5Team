from django.urls import path
from . import views

app_name = 'uauth'

urlpatterns = [
    # login 1) login page   2) login function
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
    path('email/send/', views.send_verification_email, name='send_verification_email'),
    path('email/verify/', views.verify_email_code, name='verify_email_code'),
    path('password/reset/', views.password_reset_update, name='password_reset_update'),
    path('password/change/', views.password_change, name='password_change'),
    path('withdraw/verify/', views.withdraw_verify, name='withdraw_verify'),
    path('withdraw/confirm/', views.withdraw_confirm, name='withdraw_confirm'),
]
