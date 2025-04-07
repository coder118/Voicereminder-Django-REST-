from celery import shared_task
from django.utils import timezone
from .fcm_utils import *
from django.apps import apps  # models를 직접 import하는 대신 사용
from firebase_admin import messaging
from .models import NotificationSettings, FCMToken, Sentence
import random

from typing import List
from django.http import StreamingHttpResponse
import json
import base64  # Base64 모듈 임포트
from django.utils import timezone
from .utils import *
from django.conf import settings
import redis

@shared_task
def test_task(a: int, b: int):
    print("test Celery task : ", a + b)
    return a + b

@shared_task
def test_periodic_task():
    print("test Periodic task")
    
    """Lists the available voices."""
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # cred_path2 = os.path.join(BASE_DIR, "voicereminder_app_d9862bebb234.json")
    # google_cred = service_account.Credentials.from_service_account_file(cred_path2)
    # from google.cloud import texttospeech
    # print(google_cred)
    # client = texttospeech.TextToSpeechClient(credentials=google_cred)#

    # # Performs the list voices request
    # voices = client.list_voices()

    # for voice in voices.voices:
    #     if "ko-KR" in voice.language_codes:
    #          # 한국어 목소리 추가

    #         # Display the voice's name
    #         print(f"Name: {voice.name}")

    #         # Display the supported language codes for this voice
    #         for language_code in voice.language_codes:
    #             print(f"Supported language: {language_code}")

    #         ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

    #         # Display the SSML Voice Gender
    #         print(f"SSML Voice Gender: {ssml_gender.name}")

    #         # Display the natural sample rate hertz for this voice
    #         print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")
    """[2025-04-02 13:28:22,184: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Aoede
[2025-04-02 13:28:22,185: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,186: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,187: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,187: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Charon
[2025-04-02 13:28:22,187: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,188: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,188: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,189: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Fenrir
[2025-04-02 13:28:22,190: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,191: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,192: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,192: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Kore
[2025-04-02 13:28:22,193: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,194: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,194: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,196: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Leda
[2025-04-02 13:28:22,196: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,197: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,198: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,199: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Orus
[2025-04-02 13:28:22,199: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,199: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,200: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,201: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Puck
[2025-04-02 13:28:22,202: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,202: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,203: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,203: WARNING/MainProcess] Name: ko-KR-Chirp3-HD-Zephyr
[2025-04-02 13:28:22,204: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,204: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,204: WARNING/MainProcess] Natural Sample Rate Hertz: 24000

[2025-04-02 13:28:22,205: WARNING/MainProcess] Name: ko-KR-Neural2-A
[2025-04-02 13:28:22,206: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,207: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,207: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,207: WARNING/MainProcess] Name: ko-KR-Neural2-B
[2025-04-02 13:28:22,209: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,210: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,210: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,211: WARNING/MainProcess] Name: ko-KR-Neural2-C
[2025-04-02 13:28:22,212: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,212: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,214: WARNING/MainProcess] Natural Sample Rate Hertz: 24000

[2025-04-02 13:28:22,214: WARNING/MainProcess] Name: ko-KR-Standard-A
[2025-04-02 13:28:22,215: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,215: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,216: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,217: WARNING/MainProcess] Name: ko-KR-Standard-B
[2025-04-02 13:28:22,217: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,218: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,218: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,220: WARNING/MainProcess] Name: ko-KR-Standard-C
[2025-04-02 13:28:22,220: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,221: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,222: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,223: WARNING/MainProcess] Name: ko-KR-Standard-D
[2025-04-02 13:28:22,224: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,224: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,225: WARNING/MainProcess] Natural Sample Rate Hertz: 24000

[2025-04-02 13:28:22,226: WARNING/MainProcess] Name: ko-KR-Wavenet-A
[2025-04-02 13:28:22,226: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,227: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,227: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,228: WARNING/MainProcess] Name: ko-KR-Wavenet-B
[2025-04-02 13:28:22,228: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,229: WARNING/MainProcess] SSML Voice Gender: FEMALE
[2025-04-02 13:28:22,230: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,231: WARNING/MainProcess] Name: ko-KR-Wavenet-C
[2025-04-02 13:28:22,231: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,233: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,233: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
[2025-04-02 13:28:22,234: WARNING/MainProcess] Name: ko-KR-Wavenet-D
[2025-04-02 13:28:22,234: WARNING/MainProcess] Supported language: ko-KR
[2025-04-02 13:28:22,235: WARNING/MainProcess] SSML Voice Gender: MALE
[2025-04-02 13:28:22,235: WARNING/MainProcess] Natural Sample Rate Hertz: 24000
    """
    
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
        # notification = NotificationSettings.objects.get(id=notification_id) #notification의 아이디값을 가져와서 notificaion의 외래키를 이용해서 user이름, 문장값을 가져올 수 있다.
        # user = notification.sentence.user
        # tts_voice = notification.sentence.tts_voice
        
        # 실제 알림 전송 로직
        # print(f"Sending notification to {user.username}: {notification.sentence.content}")
        
        
        send_fcm_notification(notification_id)
        
        
        # voice_mapping = {
        #     1: "ko-KR-Standard-A",
        #     2: "ko-KR-Standard-B",
        #     3: "ko-KR-Standard-C",
        #     4: "ko-KR-Standard-D"
        #     }
        
        # VoiceName = voice_mapping.get(tts_voice.id, "ko-KR-Standard-A")
        # print(VoiceName)
        
        # audio_content = generate_tts_audio(
        # text=notification.sentence.content,
        # language_code="ko-KR",
        # voice_name=VoiceName
        # )
        
        # r = redis.Redis()
        # r.publish(
        #     channel=f"user_{user.id}_tts",
        #     message=json.dumps({
        #         'audio': base64.b64encode(audio_content).decode('utf-8'),
        #         'sentence_id': notification.sentence_id
        #     })
        # )
        
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
        
