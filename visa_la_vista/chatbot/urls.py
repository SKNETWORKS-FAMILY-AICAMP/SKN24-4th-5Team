"""
URL configuration for visa_la_vista project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('interview_session_create/', views.interview_session_create, name='interview_session_create'),
    path('extract-pdf/', views.extract_pdf_view, name='extract-pdf'),
    path('chat', views.chat_list, name='chat'),
    path('interview', views.interview_page, name='interview'),
    path('api/chat/messages', views.chat_message_create, name='chat_message_create'),
    path('admission/chat/history/<str:chat_id>/', views.get_history, name='get_history'),
    path('api/chat/conversations/<str:conversation_id>/delete', views.chat_conversation_delete, name='chat_conversation_delete'),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
