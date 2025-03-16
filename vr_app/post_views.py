from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Sentence, NotificationSettings
from .serializers import CustomUserSerializer, SentenceSerializer, NotificationSettingsSerializer
from rest_framework import serializers

class CreatePostView(APIView):
    def post(self, request):
        # 요청 데이터에서 정보 추출
        sentence_data = request.data.get('sentence')
        notification_settings_data = request.data.get('notificationSettings')
        user_settings_data = request.data.get('userSettings')

        # 요청 데이터 유효성 검사
        if not sentence_data or not notification_settings_data or not user_settings_data:
            return Response({"error": "모든 필드를 제공해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 생성 또는 가져오기
        try:
            user, created = CustomUser.objects.get_or_create(
                username=request.user.username,  # 인증된 사용자 이름 사용
                defaults={
                    'vibration_enabled': user_settings_data['vibration_enabled']
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 문장 저장
        try:
            sentence_serializer = SentenceSerializer(data={
                'user': user.id,
                'content': sentence_data['content'],
                'tts_voice': sentence_data.get('tts_voice'),
                'is_ai_generated': False  # 기본값 설정
            })
            sentence_serializer.is_valid(raise_exception=True)
            sentence = sentence_serializer.save()
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 알림 설정 저장
        try:
            notification_serializer = NotificationSettingsSerializer(data={
                'sentence': sentence.id,
                'repeat_mode': notification_settings_data['repeat_mode'],
                'notification_time': notification_settings_data['notification_time'],
                'notification_date': notification_settings_data['notification_date'],
                'notification_count': notification_settings_data.get('notification_count', 1)
            })
            notification_serializer.is_valid(raise_exception=True)
            notification = notification_serializer.save()
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 성공적인 응답
        return Response({
            "message": "데이터가 성공적으로 저장되었습니다.",
            "sentence_id": sentence.id,
            "notification_id": notification.id
        }, status=status.HTTP_201_CREATED)
