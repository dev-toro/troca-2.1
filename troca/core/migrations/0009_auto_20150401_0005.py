# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.thumbs


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150331_2219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='thumbnail_url',
            field=core.thumbs.ImageWithThumbsField(upload_to=b'media/project_images/thumb'),
            preserve_default=True,
        ),
    ]
