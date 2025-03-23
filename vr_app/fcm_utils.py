from firebase_admin import messaging
from celery import shared_task
from django.utils import timezone
from .models import NotificationSettings ,FCMToken, Sentence
# def send_fcm_notification(token,title,message):
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=message,
#         ),
#         token=token,
#     )
#     try:
#         response = messaging.send(message)
#         return response
#     except Exception as e:
#         print(f"FCM 전송 실패: {e}")
#         return None
    
#@shared_task
def send_fcm_notification(notification_id):
    notification = NotificationSettings.objects.get(id=notification_id)
    user = notification.sentence.user
    fcm_token = user.fcm_token #유저에서 fcm토큰이라는 필드는 없어져서 user를 통해서fcm db로 접근해야 함

    if not fcm_token:
        return

    message = messaging.Message(
        notification=messaging.Notification(
            title="알림",
            body=notification.sentence.content
        ),
        token=fcm_token
    )

    try:
        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
        notification.is_triggered = True
        notification.save()
    except Exception as e:
        print(f"Error sending message to {user.username}: {e}")
        FCMToken.objects.filter(token=fcm_token).delete()
        user.fcm_token = None
        user.save()