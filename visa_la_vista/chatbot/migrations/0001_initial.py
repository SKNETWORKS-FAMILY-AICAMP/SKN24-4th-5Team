# Generated manually for database-backed chat and interview demo data.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_example_data(apps, schema_editor):
    AdmissionChatConversation = apps.get_model('chatbot', 'AdmissionChatConversation')
    AdmissionChatMessage = apps.get_model('chatbot', 'AdmissionChatMessage')
    VisaInterviewModeDescription = apps.get_model('chatbot', 'VisaInterviewModeDescription')
    VisaInterviewQuestion = apps.get_model('chatbot', 'VisaInterviewQuestion')

    chat_examples = [
        ('펜실베이니아 대학교 학비', '오늘'),
        ('UCLA 입학에 필요한 서류', '1일 전'),
        ('NYU SAT 점수 커트라인', '7일 전'),
    ]

    for title, group_label in chat_examples:
        conversation, _ = AdmissionChatConversation.objects.get_or_create(
            title=title,
            user=None,
            defaults={'group_label': group_label},
        )
        if not conversation.messages.exists():
            AdmissionChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content="Hello! I'm here to help you. What would you like to talk about today?",
            )

    mode_examples = {
        'practice': (
            '📝 연습 모드',
            '연습 모드는 시간 제한 없이 질문의 개수를 선택하여 진행됩니다. 질문은 텍스트와 음성으로 제공되며, 회화 연습이나 스피킹 감각을 익히려는 분들께 추천드립니다.',
        ),
        'real': (
            '🎙️ 실전 모드',
            '실전 모드는 7분 타이머가 시작되고 비자 인터뷰 질문이 자동으로 출력됩니다. 실제 면접처럼 답변을 음성으로 녹음하며 진행할 수 있습니다.',
        ),
    }

    for mode, (title, description) in mode_examples.items():
        VisaInterviewModeDescription.objects.get_or_create(
            mode=mode,
            defaults={
                'title': title,
                'description': description,
            },
        )

    questions = [
        ('practice', 1, "Hello! I'm here to help you. What would you like to talk about today?"),
        ('practice', 2, 'Why did you choose this university?'),
        ('practice', 3, 'How will you fund your studies in the United States?'),
        ('real', 1, 'Tell me about your study plan in the United States.'),
        ('real', 2, 'What ties do you have to your home country?'),
        ('real', 3, 'What will you do after graduation?'),
    ]

    for mode, order, question_text in questions:
        VisaInterviewQuestion.objects.get_or_create(
            mode=mode,
            order=order,
            defaults={'question_text': question_text},
        )


def remove_example_data(apps, schema_editor):
    AdmissionChatConversation = apps.get_model('chatbot', 'AdmissionChatConversation')
    VisaInterviewModeDescription = apps.get_model('chatbot', 'VisaInterviewModeDescription')
    VisaInterviewQuestion = apps.get_model('chatbot', 'VisaInterviewQuestion')

    AdmissionChatConversation.objects.filter(user=None).delete()
    VisaInterviewQuestion.objects.filter(mode__in=['practice', 'real']).delete()
    VisaInterviewModeDescription.objects.filter(mode__in=['practice', 'real']).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionChatConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('group_label', models.CharField(default='오늘', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admission_chat_conversations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at', '-id'],
            },
        ),
        migrations.CreateModel(
            name='VisaInterviewModeDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('practice', '연습 모드'), ('real', '실전 모드')], max_length=20, unique=True)),
                ('title', models.CharField(max_length=80)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ['mode'],
            },
        ),
        migrations.CreateModel(
            name='VisaInterviewQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('practice', '연습 모드'), ('real', '실전 모드')], max_length=20)),
                ('question_text', models.TextField()),
                ('order', models.PositiveIntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['mode', 'order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='AdmissionChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant')], max_length=20)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chatbot.admissionchatconversation')),
            ],
            options={
                'ordering': ['created_at', 'id'],
            },
        ),
        migrations.CreateModel(
            name='VisaInterviewSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('practice', '연습 모드'), ('real', '실전 모드')], max_length=20)),
                ('uploaded_file_name', models.CharField(blank=True, max_length=255)),
                ('question_count', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('ready', 'Ready'), ('in_progress', 'In Progress'), ('done', 'Done')], default='ready', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='visa_interview_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.CreateModel(
            name='VisaInterviewAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transcript', models.TextField(blank=True)),
                ('audio_label', models.CharField(blank=True, max_length=120)),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='answers', to='chatbot.visainterviewquestion')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='chatbot.visainterviewsession')),
            ],
            options={
                'ordering': ['answered_at', 'id'],
            },
        ),
        migrations.RunPython(seed_example_data, remove_example_data),
    ]
