# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150408_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='skills',
            name='slug',
            field=models.SlugField(default=datetime.datetime(2015, 4, 10, 4, 40, 16, 591222, tzinfo=utc), max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='skills_categories',
            name='slug',
            field=models.SlugField(default='slug', max_length=100),
            preserve_default=False,
        ),
    ]
