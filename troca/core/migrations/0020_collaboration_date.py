# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_project_num_needs'),
    ]

    operations = [
        migrations.AddField(
            model_name='collaboration',
            name='date',
            field=models.DateField(default=datetime.datetime(2015, 4, 19, 23, 43, 33, 588697, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
