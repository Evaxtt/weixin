# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-04 13:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_manage_plat', '0008_auto_20160204_2144'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityapplicant',
            name='money',
        ),
    ]
