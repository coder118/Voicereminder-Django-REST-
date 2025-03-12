from django.urls import path,include
from django.contrib import admin
from . import ViewSets

from rest_framework import routers
from .ViewSets import  TTSVoiceViewSet, SentenceViewSet, NotificationSettingsViewSet, AIRecommendedSentenceViewSet
from .views import RegisterView, LoginView, LogoutView,DeleteAccountView

router=routers.DefaultRouter()
router.register(r'tests',ViewSets.TestViewSet)
router.register(r'tts-voices', TTSVoiceViewSet)
router.register(r'sentences', SentenceViewSet)
router.register(r'notifications', NotificationSettingsViewSet)
router.register(r'ai-recommended-sentences', AIRecommendedSentenceViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('admin/',admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'), #회원가입하는 경로 
    path('login/', LoginView.as_view(), name='login'), #로그인 경로
    path('logout/', LogoutView.as_view(), name='logout'), #로그아웃 경로
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
]