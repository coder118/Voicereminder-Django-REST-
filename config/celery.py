from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from celery.schedules import timedelta
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vr_app.settings')

# app = Celery('vr_app')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()

# Django 설정을 로드합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Celery 구성 설정을 Django 설정에서 가져옵니다.
app.config_from_object('django.conf:settings', namespace='CELERY')



# 등록된 Django 앱에서 Celery 작업 자동 검색
app.autodiscover_tasks()  


app.conf.timezone = 'Asia/Seoul'

app.conf.beat_schedule = {
    'test_periodic_task': {
        'task': 'vr_app.tasks.test_periodic_task',
        'schedule': crontab(minute='*/3'), #timedelta(seconds=10)  #minute=1 그냥 이렇게 적으면 매 1분이라는 시각에만 동작하는 것. 8시1분 9시1분 이런식
    },
}