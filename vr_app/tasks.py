from celery import shared_task
from django.utils import timezone
from .fcm_utils import send_fcm_notification
from django.apps import apps  # models를 직접 import하는 대신 사용
from firebase_admin import messaging
from .models import NotificationSettings, FCMToken, Sentence
import random

@shared_task
def process_notifications():
    now = timezone.now()
    notifications = NotificationSettings.objects.filter(
        is_triggered=False,
        notification_date__lte=now.date(),
        notification_time__lte=now.time()
    ).select_related('sentence__user')

    for notification in notifications:
        send_fcm_notification.delay(notification.id)
        update_notification_status(notification)


def update_notification_status(notification):
    now = timezone.now()
    if notification.repeat_mode == 'once':
        notification.is_triggered = True
    elif notification.repeat_mode == 'daily':
        # 다음 날로 날짜 업데이트
        notification.notification_date = now.date() + timezone.timedelta(days=1)
    elif notification.repeat_mode == 'random':
        # 랜덤한 시간으로 업데이트 (1시간에서 24시간 사이)
        random_hours = random.randint(1, 24)
        new_time = (now + timezone.timedelta(hours=random_hours)).time()
        notification.notification_time = new_time
        if now.time() > new_time:
            # 다음 날로 설정
            notification.notification_date = now.date() + timezone.timedelta(days=1)
        else:
            notification.notification_date = now.date()
    notification.is_triggered = False
    notification.save()

# @shared_task
# def check_alarms():
#     current_time = timezone.now()
    
#     # NotificationSettings 모델 가져오기
#     NotificationSettings = apps.get_model('vr_app', 'NotificationSettings')
#     # 현재 날짜와 시간에 해당하는 알림을 찾기
#     alarms = NotificationSettings.objects.filter(is_triggered=False)
    
#     for alarm in alarms:
#         # 알림이 설정된 날짜와 시간을 조합
#         alarm_datetime = timezone.datetime.combine(alarm.notification_date, alarm.notification_time)
#         #alarm.sentence.content
#         if alarm_datetime <= current_time:
#             # 사용자에게 FCM 알림 전송
#             send_fcm_notification(alarm.sentence.user.fcm_token, "알람", "content!!!!!!")
#             alarm.is_triggered = True
#             alarm.save()

# @shared_task
# def schedule_next_check():
    
#     # NotificationSettings 모델 가져오기
#     NotificationSettings = apps.get_model('vr_app', 'NotificationSettings')
#     # 다음 알림을 찾기 위해 notification_date와 notification_time을 기준으로 정렬
#     alarms = NotificationSettings.objects.filter(is_triggered=False)

#     if alarms.exists():
#         # 가장 가까운 알림을 찾기 위해 알림 날짜와 시간을 조합
#         next_alarm = min(
#             alarms,
#             key=lambda alarm: timezone.datetime.combine(alarm.notification_date, alarm.notification_time)
#         )
        
#         next_alarm_time = timezone.datetime.combine(next_alarm.notification_date, next_alarm.notification_time)
#         delay = (next_alarm_time - timezone.now()).total_seconds()
        
#         # 다음 알림 체크를 예약
#         check_alarms.apply_async(countdown=max(0, delay))
        

# @shared_task
# def check_alarms():
#     current_time = timezone.now()
#     alarms = NotificationSettings.objects.filter(alarm_time__lte=current_time, is_triggered=False)
    
#     for alarm in alarms:
#         send_fcm_notification(alarm.sentence.user.fcm_token, "알람",alarm.sentence.content)
#         alarm.is_triggered = True
#         alarm.save()

# @shared_task
# def schedule_next_check():
#     next_alarm = NotificationSettings.objects.filter(is_triggered=False).order_by('alarm_time').first()
#     if next_alarm:
#         delay = (next_alarm.alarm_time - timezone.now()).total_seconds()
#         check_alarms.apply_async(countdown=max(0, delay))