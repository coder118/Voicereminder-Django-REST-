
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import (
    Sentence, 
    NotificationSettings,
    CustomUser
)
from .serializers import (
    SentenceSerializer,
    NotificationSettingsSerializer,
    NotificationResponseSerializer
)

class UpdateSentenceView(APIView):
    """
    문장 수정을 처리하는 커스텀 뷰
    PATCH /sentences/{id}/ 요청 처리
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            print("patch good working!!")
            # 1. 수정 대상 문장 조회 (현재 사용자 소유만)
            sentence = Sentence.objects.get(
                id=id,
                user=request.user  # 중요: 소유자 확인
            )
        except Sentence.DoesNotExist:
            return Response(
                {"error": "수정 권한이 없거나 문장이 존재하지 않습니다"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. 요청 데이터 분해
        request_data = request.data
        sentence_data = request_data.get('sentence', {})
        notification_data = request_data.get('notificationSettings', {})
        user_data = request_data.get('userSettings', {})

        # 3. 문장 본문 업데이트
        sentence_serializer = SentenceSerializer(
            instance=sentence, 
            data=sentence_data,
            partial=True
        )
        if not sentence_serializer.is_valid():
            return Response(sentence_serializer.errors, status=400)
        updated_sentence = sentence_serializer.save()

        # 4. 알림 설정 업데이트
        if notification_data.get('repeat_mode') == 'random':
            notification_data.setdefault('notification_time', None)
            notification_data.setdefault('notification_date', None)
        notification_settings = NotificationSettings.objects.get(sentence=sentence)
        notification_serializer = NotificationSettingsSerializer(
            instance=notification_settings,
            data=notification_data,
            partial=True
        )
        if not notification_serializer.is_valid():
            return Response(notification_serializer.errors, status=400)
        notification_serializer.save()

        # 5. 사용자 설정 업데이트 (TTS 음성, 진동)
        user = request.user
        user.vibration_enabled = user_data.get(
            'vibration_enabled', 
            user.vibration_enabled
        )
        # user.tts_voice_id = user_data.get(  # 모델 필드명 확인 필요 (tts_voice or tts_voice_id)
        #     'tts_voice', 
        #     user.tts_voice_id
        # )
        user.save()

        # 6. 업데이트된 데이터 직렬화
        updated_instance = NotificationSettings.objects.select_related(
            'sentence__user', 
            'sentence__tts_voice'
        ).get(sentence=sentence)

        result_serializer = NotificationResponseSerializer(updated_instance)
        
        return Response(result_serializer.data, status=status.HTTP_200_OK)
