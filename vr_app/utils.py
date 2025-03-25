from django_celery_beat.models import PeriodicTask, CrontabSchedule, ClockedSchedule
from django.utils import timezone
import json

def schedule_notification(notification):
    # 기존 PeriodicTask 삭제 update할때 
    if notification.periodic_task:
        notification.periodic_task.delete()
        
    # next_notification을 로컬 시간으로 변환 -Celery Beat는 로컬 시간을 기준으로 작업을 스케줄링하기 때문
    schedule_time = timezone.localtime(notification.next_notification)
    # utc_time = schedule_time.astimezone(timezone.utc)
    
    utc_time = notification.next_notification
    print("utils",schedule_time)
    print("utils222",schedule_time.minute,schedule_time.hour,schedule_time.day,schedule_time.month)
    print(utc_time)
      # 반복 모드에 따라 스케줄 생성
    if notification.repeat_mode == 'daily':
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=schedule_time.minute,
            hour=schedule_time.hour,
            day_of_week='*',  # 매일 실행
            day_of_month='*',
            month_of_year='*',
        )
        task = PeriodicTask.objects.create(
            crontab=schedule,
            name=f'Notification-{notification.id}',
            task='vr_app.tasks.send_notification',
            args=json.dumps([notification.id]),
        )

    elif notification.repeat_mode == 'once':
        clocked, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=utc_time
        )
        task = PeriodicTask.objects.create(
            clocked=clocked,
            name=f'Notification-{notification.id}',
            task='vr_app.tasks.send_notification',
            args=json.dumps([notification.id]),
            one_off=True,
        )
    
    # # CrontabSchedule 생성
    # schedule, _ = CrontabSchedule.objects.get_or_create(
    #     minute=schedule_time.minute,
    #     hour=schedule_time.hour,
    #     day_of_month=schedule_time.day,
    #     month_of_year=schedule_time.month,
    #     day_of_week='*' 
    # )
    # #if notification.repeat_mode == 'daily' else schedule_time.weekday(),
    # # PeriodicTask 생성
    # task = PeriodicTask.objects.create(
    #     crontab=schedule,
    #     name=f'Notification for {notification.sentence.user.username} - {notification.id}',
    #     task='vr_app.tasks.send_notification',
    #     args=json.dumps([notification.id]),
    #     one_off=notification.repeat_mode == 'once',
    # )
    #notification.repeat_mode == 'once'
    # NotificationSettings와 연결
    notification.periodic_task = task
    notification.save()
