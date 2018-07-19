# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-07-19 07:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(blank=True, max_length=100, null=True, verbose_name='Комментарий')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.Address', verbose_name='Адрес')),
            ],
        ),
        migrations.CreateModel(
            name='BuildingBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Название типа зданий')),
                ('entrance_qty', models.PositiveSmallIntegerField(default=1, verbose_name='Кол-во подъездов')),
                ('floor_qty', models.PositiveSmallIntegerField(default=5, verbose_name='Кол-во этажей')),
            ],
        ),
        migrations.CreateModel(
            name='BuildingDeviceGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buildings', models.ManyToManyField(to='sktv.Building')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entrance', models.SmallIntegerField(default=1, verbose_name='Подъезд')),
                ('floor', models.SmallIntegerField(default=1, verbose_name='Этаж')),
                ('has_ups', models.BooleanField(default=False, verbose_name='Наличие UPS')),
                ('comment', models.CharField(blank=True, max_length=100, null=True, verbose_name='Комментарии')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sktv.Building', verbose_name='Расположение')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Модель')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='Устройство')),
            ],
        ),
        migrations.AddField(
            model_name='devicemodel',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sktv.DeviceType', verbose_name='Тип устройства'),
        ),
        migrations.AddField(
            model_name='device',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sktv.DeviceModel', verbose_name='Устройство'),
        ),
        migrations.AddField(
            model_name='buildingdevicegroup',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sktv.Device'),
        ),
        migrations.AddField(
            model_name='building',
            name='base',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sktv.BuildingBase', verbose_name='Тип здания'),
        ),
        migrations.AlterUniqueTogether(
            name='building',
            unique_together=set([('base', 'address')]),
        ),
    ]
