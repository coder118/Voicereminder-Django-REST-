from django_celery_beat.models import PeriodicTask, CrontabSchedule, ClockedSchedule
from django.utils import timezone
import json
import random
import pytz
from datetime import datetime, timedelta
from google.cloud import texttospeech
from google.oauth2 import service_account
import os
from pathlib import Path


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
    
    elif notification.repeat_mode == 'random':
        
        # 1. 랜덤 시간 생성 (KST 기준)
        kst_tz = pytz.timezone('Asia/Seoul')
        random_hours = random.randint(1, 24)
        random_minutes = random.randint(0, 59)

        # 현재 KST 시간에 랜덤 델타 추가
        next_run_kst = datetime.now(kst_tz) + timedelta(
            hours=random_hours,
            minutes=random_minutes
        )
        # 2. 명시적 KST 시간 출력 (디버깅용)
        print("랜덤생성된 KST 시간:", next_run_kst)  # 예: 2025-03-27 15:30:00+09:00
        # 3. UTC 변환
        next_run_utc = next_run_kst.astimezone(pytz.UTC)
        print("랜덤변환된 UTC 시간:", next_run_utc)  # 예: 2025-03-27 06:30:00+00:00
        
        clocked, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=next_run_utc
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


#, language_code: str
def generate_tts_audio(text: str, language_code: str,voice_name: str) -> bytes:
    """Google TTS API를 사용해 오디오 생성"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    cred_path2 = os.path.join(BASE_DIR, "voicereminder_app_d9862bebb234.json")
    google_cred = service_account.Credentials.from_service_account_file(cred_path2)
    client = texttospeech.TextToSpeechClient(credentials=google_cred)
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )#language_code=language_code,
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    return response.audio_content

