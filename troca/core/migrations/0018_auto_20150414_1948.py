# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0017_collaborator'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isActive', models.BooleanField(default=False)),
                ('rate', models.IntegerField(default=0)),
                ('collaborator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('collaboratorSkill', models.ForeignKey(to='core.Skills')),
                ('project', models.ForeignKey(to='core.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='collaborator',
            name='collaborator',
        ),
        migrations.RemoveField(
            model_name='collaborator',
            name='collaboratorSkill',
        ),
        migrations.RemoveField(
            model_name='collaborator',
            name='project',
        ),
        migrations.DeleteModel(
            name='Collaborator',
        ),
    ]
