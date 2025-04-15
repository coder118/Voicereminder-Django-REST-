from firebase_admin import messaging
from celery import shared_task
from django.utils import timezone
from .models import NotificationSettings ,FCMToken, Sentence
from .models import CustomUser 

#@shared_task
def send_fcm_notification(notification_id):
    print("send_fcm_noti working")
    notification = NotificationSettings.objects.get(id=notification_id)
    user = notification.sentence.user
    print("sendfcm user",user)
    # fcm_token = user.fcm_token #유저에서 fcm토큰이라는 필드는 없어져서 user를 통해서fcm db로 접근해야 함/user가 있지만 로그인한 상태가 아닌 경우에는 실행이 될 수 없다. 
    user=CustomUser.objects.get(username=user)
    print('customuser',user) 
    print(user.fcm_tokens)
    print(user.fcm_tokens.values)
    print(user.fcm_tokens.values('token'))
    print(user.fcm_tokens.first().token)
    fcm_token = user.fcm_tokens.first().token
    print("sentence",str(notification.sentence.id))
    
    print("userid",user.id)
    # notification2 = NotificationSettings.objects.select_related(
    # 'sentence__user'  # SQL JOIN으로 한 번에 조회
    # ).get(id=notification_id)
    # if not notification2.sentence:
    #     raise ValueError("연결된 문장이 삭제됨")

    # user_id = notification2.sentence.user
    # print("userid",user_id)
    
    if not fcm_token:
        print(f"No FCM token found for user: {user.username}")
        return

    message = messaging.Message (
        notification=messaging.Notification(
            title="알림",
            body=notification.sentence.content
        ),
        token=fcm_token,
        data={
            
            "title": "알림",
            "body": notification.sentence.content,
            "click_action": "FLUTTER_NOTIFICATION_CLICK",  # Flutter에서 필수
            "notification_id": str(notification.id),  # 추가 데이터
            "user_id": str(user.id),
            "sentence_id": str(notification.sentence.id),
        },
        
        android=messaging.AndroidConfig(
            priority="high",  # 안드로이드 즉시 전송 보장
            notification=messaging.AndroidNotification(
                channel_id="high_importance_channel",  # 안드로이드 채널 ID
                click_action="FLUTTER_NOTIFICATION_CLICK",
            ),
        ),
        
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    content_available=True,  # iOS 백그라운드 처리
                    sound="default",
                ),
            ),
        )
        
    )
    
    print('message',message)
    
    try:
        #알람 전송시도 
        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
        # notification.is_triggered = True
        # notification.save()
    except NotificationSettings.DoesNotExist:
        print(f"Notification with id {notification_id} not found")
    
    except Exception as e:
        print(f"Error sending FCM notification: {e}")