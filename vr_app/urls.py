from django.urls import path,include
from django.contrib import admin
from . import ViewSets

from rest_framework import routers
from .ViewSets import  TTSVoiceViewSet, SentenceViewSet, NotificationSettingsViewSet, AIRecommendedSentenceViewSet
from .views import RegisterView, LoginView, LogoutView,DeleteAccountView,RefreshTokenView
from .post_views import CreatePostView

router=routers.DefaultRouter()
router.register(r'tests',ViewSets.TestViewSet)
router.register(r'tts-voices', TTSVoiceViewSet)
router.register(r'sentences', SentenceViewSet)
router.register(r'notifications', NotificationSettingsViewSet)
router.register(r'ai-recommended-sentences', AIRecommendedSentenceViewSet)



urlpatterns = [
    path('', include(router.urls)),#여기서 값들이 전송이 되는거네 위에서 register한 값들이
    path('admin/',admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'), #회원가입하는 경로 
    path('login/', LoginView.as_view(), name='login'), #로그인 경로
    path('logout/', LogoutView.as_view(), name='logout'), #로그아웃 경로
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    
    path('sentences/create/',CreatePostView.as_view(),name = 'sentences/create/')# 문장을 db에저장하는 경로 
]