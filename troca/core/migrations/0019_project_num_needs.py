# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150414_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='num_needs',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
