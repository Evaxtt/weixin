# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-04 02:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_manage_plat', '0002_auto_20160204_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='wx_id',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
