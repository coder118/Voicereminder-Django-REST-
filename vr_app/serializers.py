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
        fields = ['username', 'vibration_enabled']

class FcmTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['fcm_token']

class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ['user', 'content', 'tts_voice', 'is_ai_generated', 'created_at']

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = [ 'repeat_mode', 'notification_count','notification_time','notification_date']

class AIRecommendedSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendedSentence
        fields = ['content', 'category', 'created_at', 'is_active']


class NotificationCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['is_triggered']

# NotificationResponseSerializer: NotificationSettings 객체를 기준으로, 
# 연결된 Sentence와 CustomUser 정보를 함께 보내줍니다.
class NotificationResponseSerializer(serializers.ModelSerializer):
    sentence = SentenceSerializer(read_only=True)
    userSettings = CustomUserSerializer(source='sentence.user', read_only=True)
    #source='sentence.user'는 sentence 필드에서 user 속성을 참조하여 해당 사용자 정보를 가져온다.
    
    # notificationSettings 필드는 SerializerMethodField로 현재 NotificationSettings 객체의 데이터를 그대로 전달
    notificationSettings = serializers.SerializerMethodField() #사용자 정의 메서드를 통해 직렬화할 데이터를 생성할 수 있는 필드
    
    def get_notificationSettings(self, obj): 
        return NotificationSettingsSerializer(obj).data
    #obj는 현재 직렬화 중인 NotificationSettings 인스턴스
    #NotificationSettingsSerializer(obj).data는 현재 알림 설정 객체를 다시 직렬화하여 그 데이터(딕셔너리 형태)를 반환
    
    class Meta:
        model = NotificationSettings
        fields = ['id', 'sentence', 'notificationSettings', 'userSettings','is_triggered']
        
class SentenceContentSerializer(serializers.Serializer):
    content = serializers.CharField()
    tts_voice = serializers.PrimaryKeyRelatedField(queryset=TTSVoice.objects.all())

class SentenceContentUpdateSerializer(serializers.Serializer):
    content = serializers.CharField()
    tts_voice = serializers.IntegerField()


class NotificationSettingsSerializer(serializers.Serializer):
    repeat_mode = serializers.CharField()
    notification_time = serializers.TimeField(allow_null=True, required=False)
    notification_date = serializers.DateField(allow_null=True, required=False)
    is_triggered = serializers.BooleanField(required=False, default=False)
    
class UserSettingsSerializer(serializers.Serializer):
    vibration_enabled = serializers.BooleanField()

class SentenceCreateRequestSerializer(serializers.Serializer):
    sentence = SentenceContentSerializer()
    notificationSettings = NotificationSettingsSerializer()
    userSettings = UserSettingsSerializer()
    
class SentenceUpdateRequestSerializer(serializers.Serializer):
    sentence = SentenceContentUpdateSerializer()
    notificationSettings = NotificationSettingsSerializer()
    userSettings = UserSettingsSerializer()