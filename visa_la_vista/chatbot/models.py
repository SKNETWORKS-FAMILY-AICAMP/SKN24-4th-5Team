from django.db import models
from django.conf import settings


class AdmissionChatConversation(models.Model):
    title = models.CharField(max_length=120)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='admission_chat_conversations',
    )
    group_label = models.CharField(max_length=20, default='오늘')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-id']

    def __str__(self):
        return self.title


class AdmissionChatMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = (
        (ROLE_USER, 'User'),
        (ROLE_ASSISTANT, 'Assistant'),
    )

    conversation = models.ForeignKey(
        AdmissionChatConversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f'{self.conversation.title} - {self.role}'


class VisaInterviewModeDescription(models.Model):
    MODE_PRACTICE = 'practice'
    MODE_REAL = 'real'
    MODE_CHOICES = (
        (MODE_PRACTICE, '연습 모드'),
        (MODE_REAL, '실전 모드'),
    )

    mode = models.CharField(max_length=20, choices=MODE_CHOICES, unique=True)
    title = models.CharField(max_length=80)
    description = models.TextField()

    class Meta:
        ordering = ['mode']

    def __str__(self):
        return self.title


class VisaInterviewQuestion(models.Model):
    mode = models.CharField(max_length=20, choices=VisaInterviewModeDescription.MODE_CHOICES)
    question_text = models.TextField()
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['mode', 'order', 'id']

    def __str__(self):
        return self.question_text[:60]


class VisaInterviewSession(models.Model):
    STATUS_READY = 'ready'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_CHOICES = (
        (STATUS_READY, 'Ready'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_DONE, 'Done'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='visa_interview_sessions',
    )
    mode = models.CharField(max_length=20, choices=VisaInterviewModeDescription.MODE_CHOICES)
    uploaded_file_name = models.CharField(max_length=255, blank=True)
    question_count = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_READY)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'{self.get_mode_display()} - {self.status}'


class VisaInterviewAnswer(models.Model):
    session = models.ForeignKey(
        VisaInterviewSession,
        on_delete=models.CASCADE,
        related_name='answers',
    )
    question = models.ForeignKey(
        VisaInterviewQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answers',
    )
    transcript = models.TextField(blank=True)
    audio_label = models.CharField(max_length=120, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['answered_at', 'id']

    def __str__(self):
        return self.transcript[:60] or self.audio_label or 'Interview answer'


# from django.db import models
# from django import forms

# class Chat(models.Model):
#     query = models.TextField()
#     messages = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)

# class ChatForm(forms.ModelForm):
#     class Meta:
#         model = Chat
#         fields = ['query', 'messages']

# # messages = [
# #   {"role": "system", "content": "You are a helpful baking assistant."},
# #   {"role": "user", "content": "How do I bake a sourdough bread?"},
# #   {"role": "assistant", "content": "First, you need a bubbly starter..."}
# # ]


from django.db import models
 
 
# ─────────────────────────────────────────────────────────────
# 방식 1: 메시지마다 row 하나씩 저장
# 장점: 특정 메시지 조회/수정 용이, 쿼리 유연
# 단점: 대화 1세트당 INSERT 2번 (user + assistant)
# ─────────────────────────────────────────────────────────────
class ChatMessage(models.Model):
    user_id    = models.CharField(max_length=255, db_index=True)
    chat_id    = models.CharField(max_length=255, db_index=True)
    role       = models.CharField(max_length=20)   # "user" | "assistant"
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["created_at"]
 
    def __str__(self):
        return f"[{self.chat_id}] {self.role}: {self.content[:30]}"
 
 
# ─────────────────────────────────────────────────────────────
# 방식 2: chat_id 단위로 messages JSONField에 통째로 저장
# 장점: INSERT 1번, 대화 전체를 한 row에서 바로 읽음
# 단점: messages가 길어질수록 매번 전체 덮어쓰기
# ─────────────────────────────────────────────────────────────
class ChatSession(models.Model):
    user_id    = models.CharField(max_length=255, db_index=True)
    chat_id    = models.CharField(max_length=255, unique=True)
    messages   = models.JSONField(default=list)
    # messages 형태:
    # [
    #   {"role": "user",      "content": "질문"},
    #   {"role": "assistant", "content": "답변"},
    # ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["created_at"]
 
    def __str__(self):
        return f"[{self.chat_id}] {len(self.messages)}개 메시지"