# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20150402_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='highlighted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
