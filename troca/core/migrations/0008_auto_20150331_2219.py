# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150330_2345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='expire_date',
            field=models.DateField(),
            preserve_default=True,
        ),
    ]
