from django.contrib import admin

from .models import (
    AdmissionChatConversation,
    AdmissionChatMessage,
    VisaInterviewAnswer,
    VisaInterviewModeDescription,
    VisaInterviewQuestion,
    VisaInterviewSession,
)


class AdmissionChatMessageInline(admin.TabularInline):
    model = AdmissionChatMessage
    extra = 0


@admin.register(AdmissionChatConversation)
class AdmissionChatConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'group_label', 'updated_at')
    search_fields = ('title', 'messages__content')
    list_filter = ('group_label',)
    inlines = [AdmissionChatMessageInline]


@admin.register(VisaInterviewModeDescription)
class VisaInterviewModeDescriptionAdmin(admin.ModelAdmin):
    list_display = ('mode', 'title')


@admin.register(VisaInterviewQuestion)
class VisaInterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('mode', 'order', 'question_text', 'is_active')
    list_filter = ('mode', 'is_active')
    search_fields = ('question_text',)


class VisaInterviewAnswerInline(admin.TabularInline):
    model = VisaInterviewAnswer
    extra = 0


@admin.register(VisaInterviewSession)
class VisaInterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('mode', 'user', 'uploaded_file_name', 'question_count', 'status', 'created_at')
    list_filter = ('mode', 'status')
    search_fields = ('uploaded_file_name',)
    inlines = [VisaInterviewAnswerInline]
