# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-04 03:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_manage_plat', '0003_tenant_wx_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenant',
            name='wx_id',
        ),
    ]