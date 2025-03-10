from django.contrib import admin
from .models import Test,TTSVoice,CustomUser,Sentence,NotificationSettings,PasswordChangeLog,AIRecommendedSentence
# Register your models here.
admin.site.register(Test)
admin.site.register(TTSVoice)
admin.site.register(CustomUser)
admin.site.register(Sentence)
admin.site.register(NotificationSettings)
admin.site.register(PasswordChangeLog)
admin.site.register(AIRecommendedSentence)
