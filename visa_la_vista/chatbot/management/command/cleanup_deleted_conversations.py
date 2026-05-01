from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chatbot.models import AdmissionChatConversation

class Command(BaseCommand):
    help = '6개월 지난 삭제 대화방 실제 삭제'

    def handle(self, *args, **kwargs):
        six_months_ago = timezone.now() - timedelta(days=180)
        count, _ = AdmissionChatConversation.objects.filter(
            is_deleted=True,
            deleted_at__lte=six_months_ago
        ).delete()
        self.stdout.write(f"실제 삭제 완료: {count}개")