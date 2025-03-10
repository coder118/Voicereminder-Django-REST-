from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

class Test(models.Model):
    test=models.CharField(max_length=10)
    
    def __str__(self):
        return self.test
    

# TTSVoice 모델
class TTSVoice(models.Model):
    """TTS 음성 옵션"""
    name = models.CharField(max_length=50, unique=True)  # 음성 이름
    language = models.CharField(max_length=20)  # 언어 (예: ko-KR, en-US)
    style = models.CharField(max_length=20, blank=True)  # 음성 스타일 (선택 사항)

    def __str__(self):
        return f"{self.name} ({self.language})"


# CustomUser 모델
class CustomUser(AbstractUser):
    """사용자 정보 확장"""
    tts_voice = models.ForeignKey(
        TTSVoice, on_delete=models.SET_NULL, null=True, blank=True
    )  # 외래키로 TTSVoice 참조
    vibration_enabled = models.BooleanField(default=True)  # 진동 알림 설정

    # groups와 user_permissions 필드에 related_name 추가
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",
        related_query_name="user",
    )
    
    def __str__(self):
        return self.username


# Sentence 모델
class Sentence(models.Model):
    """사용자가 작성한 문장 및 알림 데이터"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 사용자와 연결
    content = models.TextField()  # 문장 내용
    is_ai_generated = models.BooleanField(default=False)  # AI 추천 여부
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"


# NotificationSettings 모델
class NotificationSettings(models.Model):
    """알림 설정"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # 사용자와 연결
    repeat_mode = models.CharField(
        max_length=10,
        choices=[('once', '한번'), ('daily', '매일'), ('random', '랜덤')],
        default='once'
    )  # 반복 설정
    notification_count = models.PositiveIntegerField(default=1)  # 알림 횟수 제한
    notification_time = models.TimeField(null=True, blank=True)  # 알림 시간
    notification_date = models.DateField(null=True, blank=True)  # 알림 날짜
#아마 여기에 시간을 직접 설정을 할 수 있는 속성값을 넣어야 할 것으로 보임
    def __str__(self):
        date_str = self.notification_date.strftime("%Y-%m-%d") if self.notification_date else "No date set" #날짜 값이 비어있을때 no date 반환
        time_str = self.notification_time.strftime("%H:%M") if self.notification_time else "No time set" #알람 시간이 안 정해져 있을 경우 
        return f"{self.user.username}: {self.repeat_mode} on {date_str} at {time_str}"


# PasswordChangeLog 모델
class PasswordChangeLog(models.Model):
    """비밀번호 변경 기록"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.changed_at}"


class AIRecommendedSentence(models.Model):
    """AI가 추천한 문장"""
    content = models.TextField()  # 추천 문장 내용
    category = models.CharField(max_length=50)  # 카테고리 (예: 동기 부여, 휴식 등)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    is_active = models.BooleanField(default=True)  # 활성화 여부 (비활성화된 문장은 제외)
    
    def __str__(self):
        return f"{self.category}: {self.content[:20]}"