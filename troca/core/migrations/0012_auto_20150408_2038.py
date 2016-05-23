# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import froala_editor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_project_highlighted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='content',
            field=froala_editor.fields.FroalaField(),
            preserve_default=True,
        ),
    ]
