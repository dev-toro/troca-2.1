# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='summary',
            field=models.TextField(max_length=400),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='about',
            field=models.TextField(max_length=400),
            preserve_default=True,
        ),
    ]
