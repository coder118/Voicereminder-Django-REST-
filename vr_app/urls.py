from django.urls import path,include
from django.contrib import admin
from . import ViewSets

from rest_framework import routers
from .ViewSets import  TTSVoiceViewSet, SentenceViewSet, NotificationSettingsViewSet, AIRecommendedSentenceViewSet,SentenceNotificationViewSet
from .views import RegisterView, LoginView, LogoutView,DeleteAccountView,RefreshTokenView,UpdateFcmTokenView,changeText_to_TTS
from .post_views import CreatePostView
from .getSentence_views import GetSentenceView
from .update_views import UpdateSentenceView
from .views import Test

router=routers.DefaultRouter()
router.register(r'tests',ViewSets.TestViewSet)

# router.register(r'sentences', SentenceViewSet)
# router.register(r'notifications', NotificationSettingsViewSet)
router.register(r'ai-recommended-sentences', AIRecommendedSentenceViewSet)

router.register(r'tts-voices', TTSVoiceViewSet,basename='ttsvoice')
router.register(r'notifications', SentenceNotificationViewSet, basename='notification') # get
router.register(r'sentences', SentenceNotificationViewSet, basename='sentence') #patch 


urlpatterns = [
    path('', include(router.urls)),#여기서 값들이 전송이 되는거네 위에서 register한 값들이
    path('admin/',admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'), #회원가입하는 경로 
    path('login/', LoginView.as_view(), name='login'), #로그인 경로
    path('logout/', LogoutView.as_view(), name='logout'), #로그아웃 경로
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    
    path('update_fcm_token/', UpdateFcmTokenView.as_view(), name='update_fcm_token'), # 토큰 업데이트 
    path('sentences_create/',CreatePostView.as_view(),name = 'create_sentence'),# 문장을 db에저장하는 경로 
    # path('notifications_check/', GetSentenceView.as_view(), name='notifications_check'), 문장 get
    # path('sentence/<int:id>/', UpdateSentenceView.as_view(), name='update_sentence'), 문장 update
    
    path('tts/sentence/', changeText_to_TTS.as_view(), name='text-to-tts'),
    
    path('test', Test.as_view()),
]