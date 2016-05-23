# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150410_0441'),
    ]

    operations = [
        migrations.AddField(
            model_name='skills',
            name='description',
            field=models.TextField(default='Hola amigos mios', max_length=500),
            preserve_default=False,
        ),
    ]
