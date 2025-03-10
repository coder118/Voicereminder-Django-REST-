from rest_framework import viewsets

from .models import Test
from .serializers import TestSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

from rest_framework import viewsets
from .models import TTSVoice, Sentence, NotificationSettings, AIRecommendedSentence
from .serializers import TTSVoiceSerializer, SentenceSerializer, NotificationSettingsSerializer, AIRecommendedSentenceSerializer

class TTSVoiceViewSet(viewsets.ModelViewSet):
    queryset = TTSVoice.objects.all()
    serializer_class = TTSVoiceSerializer

class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

class NotificationSettingsViewSet(viewsets.ModelViewSet):
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer

class AIRecommendedSentenceViewSet(viewsets.ModelViewSet):
    queryset = AIRecommendedSentence.objects.filter(is_active=True)  # 활성화된 문장만 반환
    serializer_class = AIRecommendedSentenceSerializer
   