from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vr_app.settings')

# app = Celery('vr_app')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()

# Django 설정을 로드합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('vr_app')

# Celery 구성 설정을 Django 설정에서 가져옵니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 등록된 Django 앱에서 Celery 작업 자동 검색
app.autodiscover_tasks()  