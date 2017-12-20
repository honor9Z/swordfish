# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-20 02:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=23, verbose_name='部门名称')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='角色标题')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='姓名')),
                ('email', models.CharField(max_length=32, verbose_name='邮箱')),
                ('gender', models.IntegerField(choices=[(1, '男'), (2, '女'), (3, '少伟')], verbose_name='性别')),
                ('depart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app04.Department', verbose_name='所属部门')),
                ('roles', models.ManyToManyField(to='app04.Role', verbose_name='扮演的角色')),
            ],
        ),
    ]
