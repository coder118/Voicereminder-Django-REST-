from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import CustomUserSerializer

class RegisterView(APIView):
    """회원가입"""
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
                username=serializer.validated_data['username'],
                password=request.data.get('password'),  # 비밀번호는 별도로 처리
                tts_voice=serializer.validated_data.get('tts_voice'),
                vibration_enabled=serializer.validated_data.get('vibration_enabled', True)
            )
            return Response({"message": "회원가입 성공"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """로그인"""
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
                "tts_voice": user.tts_voice.name if user.tts_voice else None,
                "vibration_enabled": user.vibration_enabled,
            }, status=status.HTTP_200_OK)
        return Response({"error": "로그인 실패. 아이디 또는 비밀번호를 확인하세요."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """로그아웃"""
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # 토큰을 블랙리스트에 추가하여 무효화
            return Response({"message": "로그아웃 성공"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "로그아웃 실패"}, status=status.HTTP_400_BAD_REQUEST)
