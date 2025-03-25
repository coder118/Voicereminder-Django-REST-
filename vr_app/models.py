from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
# Create your models here.

class Test(models.Model):
    test=models.CharField(max_length=10)
    
    def __str__(self):
        return self.test
    

# TTSVoice 모델
class TTSVoice(models.Model):
    """TTS 음성 옵션"""
    name = models.CharField(max_length=50, unique=True)  # 음성 이름
    description = models.TextField(blank=True)  # 음성 스타일 (선택 사항)
    voice_id = models.CharField("서비스 ID", max_length=100,default = 1)  # Google TTS Voice ID 추가, default값을 추가하면 좋지 않음 나중에 수정을 하는 코드를 구성해줘야함
    language = models.CharField(max_length=10, default='ko-KR')  # 언어 코드 추가

    def __str__(self):
        return f"{self.name} ({self.language})" 

class FCMToken(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

# CustomUser 모델
class CustomUser(AbstractUser):
    """사용자 정보 확장"""
    
    vibration_enabled = models.BooleanField(default=True)  # 진동 알림 설정
    #fcm_token = models.CharField(max_length=255, blank=True, null=True)
    
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
    
    tts_voice = models.ForeignKey(
        TTSVoice, on_delete=models.SET_NULL, null=True, blank=True
    )  # 외래키로 TTSVoice 참조
    
    is_ai_generated = models.BooleanField(default=False)  # AI 추천 여부
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # 생성 시간 
    # 시간순 정렬: 최신 문장 먼저 보여주기 /통계 분석: 사용자의 문장 작성 패턴 파악/ 기간별 필터링: "이번 달에 작성한 문장만 보기" 등
    def clean(self):
        
        queryset = Sentence.objects.filter(user=self.user, content=self.content)
        if self.pk:  # 객체가 이미 DB에 저장된 경우 (업데이트)
            queryset = queryset.exclude(pk=self.pk)
        
        if queryset.exists():
            raise ValidationError("이미 동일한 내용의 문장이 존재합니다.")

    def save(self, *args, **kwargs):
        self.full_clean()  # 유효성 검사 호출
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"


# NotificationSettings 모델
class NotificationSettings(models.Model):
    """알림 설정"""
    sentence = models.OneToOneField(Sentence, on_delete=models.CASCADE)  # 문장과 연결을 해서 1:n의 관계를 만듬 문장 하나에 여러개의 알림이 가능
    
    periodic_task = models.OneToOneField( #beat의 PeriodicTask값을 저장한다. 
        'django_celery_beat.PeriodicTask',
        on_delete=models.SET_NULL,#관련 PeriodicTask가 삭제되면 이 필드는 NULL로 설정
        null=True,
        blank=True
    )
    
    repeat_mode = models.CharField(
        max_length=10,
        choices=[('once', '한번'), ('daily', '매일'), ('random', '랜덤')],
        default='once'
    )  # 반복 설정
    notification_count = models.PositiveIntegerField(default=1)  # 알림 횟수 제한
    notification_time = models.TimeField(null=True, blank=True)  # 알림 시간
    notification_date = models.DateField(null=True, blank=True)  # 알림 날짜
#아마 여기에 시간을 직접 설정을 할 수 있는 속성값을 넣어야 할 것으로 보임
    next_notification = models.DateTimeField(null=True, blank=True)  # 다음 알림 시간
    is_triggered = models.BooleanField(default=False)  # 알림 트리거 여부
    def __str__(self):
        date_str = self.notification_date.strftime("%Y-%m-%d") if self.notification_date else "No date set" #날짜 값이 비어있을때 no date 반환
        time_str = self.notification_time.strftime("%H:%M") if self.notification_time else "No time set" #알람 시간이 안 정해져 있을 경우 
        return f"{self.sentence.user.username}: {self.repeat_mode} on {date_str} at {time_str}"


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