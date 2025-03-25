from django.contrib import admin
from .models import Test,TTSVoice,CustomUser,Sentence,NotificationSettings,PasswordChangeLog,AIRecommendedSentence,FCMToken
from django.utils import timezone
# Register your models here.
admin.site.register(Test)
admin.site.register(TTSVoice)
admin.site.register(CustomUser)
admin.site.register(Sentence)
admin.site.register(NotificationSettings)
admin.site.register(PasswordChangeLog)
admin.site.register(AIRecommendedSentence)
admin.site.register(FCMToken)

def save_model(self, request, obj, form, change):
    if timezone.is_naive(obj.next_notification):  # 시간대 정보 없는 경우
        local_tz = timezone.get_current_timezone()
        obj.next_notification = local_tz.localize(obj.next_notification)  # KST로 명시적 변환
    
    obj.next_notification = obj.next_notification.astimezone(timezone.utc)  # UTC 변환
    super().save_model(request, obj, form, change)
