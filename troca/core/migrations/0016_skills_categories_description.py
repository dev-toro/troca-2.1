# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_skills_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='skills_categories',
            name='description',
            field=models.TextField(default='Esta es la descripcion de una categoaegoria\x08\x08', max_length=500),
            preserve_default=False,
        ),
    ]
