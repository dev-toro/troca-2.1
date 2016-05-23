# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150401_0005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='video_url',
        ),
        migrations.AddField(
            model_name='project',
            name='slug',
            field=models.SlugField(default='orihext', unique=True, max_length=100),
            preserve_default=False,
        ),
    ]
