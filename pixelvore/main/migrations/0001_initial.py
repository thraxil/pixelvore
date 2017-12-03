# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('url', models.URLField(default=b'')),
                ('ahash', models.CharField(default=b'', max_length=256, null=True)),
                ('ext', models.CharField(default=b'.jpg', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='ImageTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ForeignKey(to='main.Image', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('tag', models.CharField(default=b'', max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='imagetag',
            name='tag',
            field=models.ForeignKey(to='main.Tag', on_delete=models.CASCADE),
        ),
    ]
