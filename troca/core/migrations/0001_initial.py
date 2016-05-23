# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('date', models.DateField(auto_now_add=True)),
                ('expire_date', models.DateTimeField()),
                ('summary', models.CharField(max_length=400)),
                ('content', models.TextField()),
                ('thumbnail_url', models.ImageField(upload_to=b'project_thumbs', blank=True)),
                ('rate', models.IntegerField(default=0)),
                ('video_url', models.URLField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Skills_categories',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('facebook', models.URLField(blank=True)),
                ('twitter', models.URLField(blank=True)),
                ('rate', models.IntegerField(default=0)),
                ('about', models.CharField(max_length=400)),
                ('date', models.DateField(auto_now_add=True)),
                ('avatar_url', models.ImageField(upload_to=b'profile_images', blank=True)),
                ('category', models.ManyToManyField(to='core.Skills')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='skills',
            name='category',
            field=models.ForeignKey(to='core.Skills_categories'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='category',
            field=models.ManyToManyField(to='core.Skills'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
