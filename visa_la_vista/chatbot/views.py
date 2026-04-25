from django.shortcuts import render, redirect
# from .models import Question, Answer, QuestionForm
from django.http import Http404, HttpResponseForbidden 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import resolve_url
from django.http import JsonResponse


# Create your views here.

@login_required(login_url='uauth:login')
def chat_list(request):
    return render(request, 'chatbot/chat_page.html') #, {'page_obj': page_obj}

@login_required(login_url='uauth:login')
def interview_page(request):
    return render(request, 'chatbot/interview_page.html') #, {'page_obj': page_obj}
