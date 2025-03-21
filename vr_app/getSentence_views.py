from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import NotificationSettings
from .serializers import NotificationResponseSerializer

class GetSentenceView(APIView):
    permission_classes = [IsAuthenticated]
    print("getsentence@!!!!!!")
    def get(self, request, format=None):
        # 로그인한 사용자의 문장에 연결된 알림만 선택 (Sentence의 user 필드를 기준으로)
        # notifications = NotificationSettings.objects.filter(sentence__user=request.user)
        # serializer = NotificationResponseSerializer(notifications, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        try:
            print("getsentence try ")
            # 현재 로그인한 사용자의 문장 알림만 반환
            notifications = NotificationSettings.objects.filter(sentence__user=request.user)
            print('getsentence nofification',notifications)
            serializer = NotificationResponseSerializer(notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("get sentence ",e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
