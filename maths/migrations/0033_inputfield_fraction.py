# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-26 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0032_auto_20170726_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputfield',
            name='fraction',
            field=models.BooleanField(default=False),
        ),
    ]