# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.thumbs


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar_url',
            field=core.thumbs.ImageWithThumbsField(upload_to=b'media/profile_images/thumb'),
            preserve_default=True,
        ),
    ]
