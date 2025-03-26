from celery import shared_task
from django.utils import timezone
from .fcm_utils import send_fcm_notification
from django.apps import apps  # models를 직접 import하는 대신 사용
from firebase_admin import messaging
from .models import NotificationSettings, FCMToken, Sentence
import random

from typing import List

from django.utils import timezone
from .utils import schedule_notification

@shared_task
def test_task(a: int, b: int):
    print("test Celery task : ", a + b)
    return a + b

@shared_task
def test_periodic_task():
    print("test Periodic task")
    return "Complete"


#false이고 notification에 저장된 유저의 date와 time값을 가져오고 그때만 celery가 실행이 된다? 예약을 해두는 느낌이면 가능하지 않을까? celery beat는 원하는 시간을 설정을 해둘 수 있으니까
#user가 notification에 값을 저장할때 바로 그 시간을 celery beat로 예약을 해두는 느낌으로 저장을 하면 그 시간에 celery동작. false값은 true로 바꿔준다. 
#근데 그럼 모든 알람이 저장이 되어야 하면 celery beat자체에 부담이 되는건 아닌지? 애초에 여러개의 알림을 동시에 저장을 할 수 있을까? 최대 몇개?
#취소하거나 수정할때의 값도 추가를 해줘야 한다. 
@shared_task
def send_notification(notification_id):
    print("what the celery working?")
    try:
        print("check celery task")
        notification = NotificationSettings.objects.get(id=notification_id) #notification의 아이디값을 가져와서 notificaion의 외래키를 이용해서 user이름, 문장값을 가져올 수 있다.
        user = notification.sentence.user
        
        
        # 실제 알림 전송 로직
        print(f"Sending notification to {user.username}: {notification.sentence.content}")
        
        
        send_fcm_notification(notification_id)
        
        # 여기에 실제 알림 전송 코드 추가 (예: FCM)
        
        # # 반복 모드 처리
        # if notification.repeat_mode == 'once':
        #     notification.is_triggered = True
        #     notification.save()
        #     if notification.periodic_task:
        #         notification.periodic_task.delete()
        # elif notification.repeat_mode == 'daily':
        #     next_run = timezone.localtime(timezone.now()) + timezone.timedelta(days=1)
        #     notification.next_notification = next_run
        #     notification.save()
        #     if notification.periodic_task:
        #         notification.periodic_task.crontab.day_of_month = '*'
        #         notification.periodic_task.crontab.save()
        # elif notification.repeat_mode == 'random':
        #     import random
        #     next_run = timezone.localtime(timezone.now()) + timezone.timedelta(
        #         hours=random.randint(1, 24),
        #         minutes=random.randint(0, 59)
        #     )
        #     notification.next_notification = next_run
        #     notification.save()
        #     schedule_notification(notification)
        
    except NotificationSettings.DoesNotExist:
        print(f"Notification with id {notification_id} not found")

# @shared_task
# def process_notifications():
#     now = timezone.now() #현재 시각 입력 + 저장된 date값과 시간값을 1분마다 현재 시각이랑 비교를 했을때 알람이 실행이 되지 않았고(false) 일치하는 값이 있을때만 실행-> 너무 서버 부담이 커지지 않나?
#     notifications = NotificationSettings.objects.filter(# 알람시간의 값을 filter로 구분을 해서 가지고 오는데 related되어있는게 단순히 user를 가져오는게 아니라 로그인되어있는 user를 가지고 와야함.
#         is_triggered=False,
#         notification_date__lte=now.date(),
#         notification_time__lte=now.time()
#     ).select_related('sentence__user')

#     for notification in notifications:
#         send_fcm_notification.delay(notification.id)
#         update_notification_status(notification)



# def update_notification_status(notification):
#     now = timezone.now()
#     if notification.repeat_mode == 'once':
#         notification.is_triggered = True
#     elif notification.repeat_mode == 'daily':
#         # 다음 날로 날짜 업데이트
#         notification.notification_date = now.date() + timezone.timedelta(days=1)
#     elif notification.repeat_mode == 'random':
#         # 랜덤한 시간으로 업데이트 (1시간에서 24시간 사이)
#         random_hours = random.randint(1, 24)
#         new_time = (now + timezone.timedelta(hours=random_hours)).time()
#         notification.notification_time = new_time
#         if now.time() > new_time:
#             # 다음 날로 설정
#             notification.notification_date = now.date() + timezone.timedelta(days=1)
#         else:
#             notification.notification_date = now.date()
#     notification.is_triggered = False
#     notification.save()
######################### 위에거 사용 
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