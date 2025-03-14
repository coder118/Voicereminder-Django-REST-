# Generated by Django 4.2.20 on 2025-03-14 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vr_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationsettings',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='vr_app.sentence'),
        ),
        migrations.AlterField(
            model_name='sentence',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
