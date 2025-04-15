from rest_framework import viewsets

from .models import Test
from .serializers import TestSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


from .models import TTSVoice, Sentence, NotificationSettings, AIRecommendedSentence
from .serializers import TTSVoiceSerializer, SentenceSerializer, NotificationSettingsSerializer, AIRecommendedSentenceSerializer,NotificationResponseSerializer,SentenceCreateRequestSerializer,SentenceUpdateRequestSerializer,NotificationCheckSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status
from .utils import schedule_notification
from django.utils import timezone
from datetime import datetime
import pytz

class TTSVoiceViewSet(viewsets.ModelViewSet):
    queryset = TTSVoice.objects.all()
    serializer_class = TTSVoiceSerializer
    
    @action(detail=False, methods=['get'])
    def list_voices(self, request):
        voices = TTSVoice.objects.all()
        serializer = self.get_serializer(voices, many=True)
        return Response(serializer.data)

class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

class NotificationSettingsViewSet(viewsets.ModelViewSet):
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer

class AIRecommendedSentenceViewSet(viewsets.ModelViewSet):
    queryset = AIRecommendedSentence.objects.filter(is_active=True)  # 활성화된 문장만 반환
    serializer_class = AIRecommendedSentenceSerializer

class NotificationCheckViewSet(viewsets.ModelViewSet): #알람이 실행되면 is triggered를 true로 바꿔주고 update할시에는 다시 false로 바꿔준다. 
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationCheckSerializer

    @action(detail=True, methods=['patch'], url_path='update-trigger')
    def update_trigger(self, request, pk=None):
        notification = self.get_object()
        serializer = self.get_serializer(notification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class SentenceNotificationViewSet(viewsets.ModelViewSet): # 여기서 get, post, delete,patch가능하다. 
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationSettings.objects.filter(
            sentence__user=self.request.user
        ).select_related(
            'sentence', 'sentence__user', 'sentence__tts_voice'
        )
    
    @action(detail=False, methods=['post'])
    def create_sentence(self, request):
        serializer = SentenceCreateRequestSerializer(data=request.data)
        print("post function",serializer)
         # 유효성 검사 실패 시 오류 출력
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            # Sentence 생성
            sentence_data = serializer.validated_data['sentence']
            notification_data = serializer.validated_data['notificationSettings']
            user_settings_data = serializer.validated_data['userSettings']

            
            sentence = Sentence.objects.create(
                user=request.user,
                content=sentence_data['content'],
                tts_voice=sentence_data['tts_voice'] 
            )


            kst_tz = pytz.timezone('Asia/Seoul')
            
            # 명시적으로 KST로 변환
            kst_time = kst_tz.localize(datetime.combine(
                notification_data.get('notification_date'),
                notification_data.get('notification_time')
            ))
            print("명시적 KST 시간:", kst_time)  # 2025-03-25 13:54:00+09:00
            
            #  UTC 변환
            utc_time = kst_time.astimezone(pytz.UTC)
            print("UTC 시간:", utc_time)
            
            notification = NotificationSettings.objects.create(
                sentence=sentence,
                repeat_mode=notification_data['repeat_mode'],
                notification_time=notification_data.get('notification_time'),
                notification_date=notification_data.get('notification_date'),
                next_notification=utc_time
            )
            
            schedule_notification(notification)#celery beat에 바로 스케줄링을 해준다.
            
            # UserSettings 업데이트
            request.user.vibration_enabled = user_settings_data['vibration_enabled']
            request.user.save()

            return Response(NotificationResponseSerializer(notification).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        notifications = self.get_queryset()
        serializer = NotificationResponseSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_sentence(self, request, pk=None):
        notification = self.get_object()
        
        print("update?", notification)
        
        if notification.sentence.user != request.user:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SentenceUpdateRequestSerializer(data=request.data, partial=True)
        
        print("serializer=sentencecreaterequest",serializer)
        if serializer.is_valid():
            print("throgh? serializer?")
            sentence_data = serializer.validated_data.get('sentence', {})
            notification_data = serializer.validated_data.get('notificationSettings', {})
            user_settings_data = serializer.validated_data.get('userSettings', {})
            
            
            # Update sentence
            sentence = notification.sentence
            print('notification.sentence@@@@@@@@@',sentence)
            for attr, value in sentence_data.items():
                if attr == 'tts_voice':
                    try:
                        tts_voice = TTSVoice.objects.get(id=value)
                        sentence.tts_voice = tts_voice
                    except TTSVoice.DoesNotExist:
                        return Response({"error": "Invalid TTS voice ID"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    setattr(sentence, attr, value)
            sentence.save()

                # Update notification settings
            for attr, value in notification_data.items():
                setattr(notification, attr, value)
            
            if 'notification_time' in notification_data or 'notification_date' in notification_data: # next_notification을 저장해준다. timezone.make_aware을 이용해서 Aware datetime 객체사용 이유는 django는 기본적으로 UTC 시간대를 사용
                kst_tz = pytz.timezone('Asia/Seoul')
                
                #  명시적으로 KST로 변환
                kst_time = kst_tz.localize(datetime.combine(
                    notification_data.get('notification_date'),
                    notification_data.get('notification_time')
                ))
                print("명시적 KST 시간:", kst_time)  # 2025-03-25 13:54:00+09:00
                
                #  UTC 변환
                utc_time = kst_time.astimezone(pytz.UTC)
                print("UTC 시간:", utc_time)
                
                notification.next_notification=utc_time
                
            schedule_notification(notification) #업데이트시에도 재스케줄링
            
                # Update user settings
            user = request.user
            if 'vibration_enabled' in user_settings_data:
                user.vibration_enabled = user_settings_data['vibration_enabled']
                user.save()

            print("check trigger update",notification.is_triggered)
            return Response(NotificationResponseSerializer(notification).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_sentence(self, request, pk=None):
        notification = self.get_object()
        
        print('delete working?',notification)
        
        # 권한 확인
        if notification.sentence.user != request.user:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if notification.periodic_task:#알림 설정 지우기 
            notification.periodic_task.delete()
        
        try:
            # 연관된 Sentence 객체 삭제
            sentence = notification.sentence
            print('delete sentence check',sentence)
            sentence.delete()  # 이는 CASCADE 설정으로 인해 NotificationSettings도 함께 삭제됩니다.

            return Response({"message": "문장이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)