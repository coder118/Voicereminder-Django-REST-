from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,FCMToken
from .serializers import CustomUserSerializer,FcmTokenSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
#from django.http import HttpResponse
from rest_framework_simplejwt.exceptions import TokenError
import logging

# logger = logging.getLogger('django')

class RegisterView(APIView):
    """회원가입"""
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)#여기서 시리얼라이즈를 사용 회원가입 창에서 보낸 입력값을 시리얼라이즈로
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
                username=serializer.validated_data['username'],
                password=request.data.get('password'),  # 비밀번호는 별도로 처리
                #tts_voice=serializer.validated_data.get('tts_voice'), 회원가입창에 tts 부분을 제거해줘야 함!!!!
                vibration_enabled=serializer.validated_data.get('vibration_enabled', True)
            )
            return Response({"message": "회원가입 성공"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#https://stackoverflow.com/questions/59856341/okhttp-http-failed-java-net-unknownserviceexception-cleartext-communicati
#https://ethank.tistory.com/entry/django-%EC%84%9C%EB%B2%84-%ED%8F%AC%ED%8A%B8%EB%B2%88%ED%98%B8-%EB%B0%94%EA%BE%B8%EA%B8%B0-%EB%B0%8F-%EC%99%B8%EB%B6%80-%EC%A0%91%EC%86%8D-%ED%97%88%EC%9A%A9
class LoginView(APIView):
    """로그인"""
    # logger.debug(f"🚀 로그인 요청: {method} FROM {request.META.get('REMOTE_ADDR')}")
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        fcm_token = request.data.get('fcm_token')
        print(f"Username: {username}, Password: {password},fcmtoken{fcm_token}")
       
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            # FCM 토큰 업데이트
            # if fcm_token:
            #     user.fcm_token = fcm_token
            #     user.save()
            # FCM 토큰 저장 또는 업데이트
            if fcm_token:
                FCMToken.objects.get_or_create(user=user, token=fcm_token)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
                #"tts_voice": user.tts_voice.name if user.tts_voice else 0,
                #"fcm_token": user.fcm_token, 
                "vibration_enabled": user.vibration_enabled,
            }, status=status.HTTP_200_OK)
        return Response({"error": "로그인 실패. 아이디 또는 비밀번호를 확인하세요."}, status=status.HTTP_401_UNAUTHORIZED)
    
   
#@method_decorator(csrf_exempt, name='dispatch')
#@csrf_exempt
class LogoutView(APIView):
    # permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  # JWT 인증 클래스 추가
    permission_classes = [IsAuthenticated]
    """로그아웃"""
    print("fun")
    def post(self, request):
        print("Headers:", request.headers)
        print("Body:", request.data)
        try:
            
            FCMToken.objects.filter(user=request.user).delete()#로그아웃시 로그인시 만들었던 fmctoken삭제 
            
            print("logout?")
            refresh_token = request.data.get("refresh")
            print("Refresh token:", refresh_token)
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token) 
            token.blacklist()  # 토큰을 블랙리스트에 추가하여 무효화
            #RefreshToken(refresh_token).delete()
            
            # FCM 토큰 연결 끊기 (비활성화 처리)
            # user = request.user
            # user.fcm_token = None  # FCM 토큰을 제거하지 않고 연결만 끊음
            # user.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        #HttpResponse(status=status.HTTP_205_RESET_CONTENT, content_type=None)  Response({"message": "로그아웃 성공"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e: 
            print("logout fail",str(e))
            return Response({"error": "로그아웃 실패"}, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):#로그인시 리프레쉬 토큰과 액세스 토큰이 만료되었을시 해결을 해주는 클래스
    def post(self, request):
        print("checking refresh token")
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            
            token = RefreshToken(refresh_token) #리프레쉬 토큰의 유효성검사 좋게 실행된다면 액세스토큰 생성
            access_token = str(token.access_token)
            print("you have refresh token")
            return Response({
                "access": access_token
            }, status=status.HTTP_200_OK)

        except TokenError as e: #리프레쉬 토큰도 없을경우 오류를 돌려줘서 로그인화면으로 돌아가게 시킴
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print("delete",user)
        
        # FCM 토큰 제거
        # user.fcm_token = None
        # user.save()
        
        user.delete()
        return Response({"message": "계정이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
    
   
    
class UpdateFcmTokenView(APIView): # fcm 토큰을 유저에 fcm_token 필드에 저장
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_profile = CustomUser.objects.get(user=request.user)
            serializer = FcmTokenSerializer(user_profile, data=request.data, partial=True)
        
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)    
    
