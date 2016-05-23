# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150310_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='thumbnail_url',
            field=models.ImageField(upload_to=b'/media/project_thumbs', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar_url',
            field=models.ImageField(upload_to=b'/media/profile_images', blank=True),
            preserve_default=True,
        ),
    ]
