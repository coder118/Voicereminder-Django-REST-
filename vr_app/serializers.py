from rest_framework import serializers
from .models import Test

class TestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Test
        fields = ['test','id']

from rest_framework import serializers
from .models import TTSVoice, CustomUser, Sentence, NotificationSettings, AIRecommendedSentence
#data를 json형태로 변경을 해주는 과정 이렇게 바꾸고 url.py에서 값을 보낸다. 
class TTSVoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTSVoice
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'tts_voice', 'vibration_enabled']

class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ['user', 'content', 'is_ai_generated', 'created_at']

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['user', 'repeat_mode', 'notification_count','notification_time','notification_date']

class AIRecommendedSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendedSentence
        fields = ['content', 'category', 'created_at', 'is_active']
