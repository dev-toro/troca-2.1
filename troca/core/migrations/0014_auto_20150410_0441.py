# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20150410_0440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skills',
            name='slug',
            field=models.SlugField(unique=True, max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='skills_categories',
            name='slug',
            field=models.SlugField(unique=True, max_length=100),
            preserve_default=True,
        ),
    ]
