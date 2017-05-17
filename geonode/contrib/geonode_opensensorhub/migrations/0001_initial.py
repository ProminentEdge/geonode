# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '24_initial'),
        ('base', '24_to_26'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapSensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('map', models.ForeignKey(to='maps.Map')),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('resourcebase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base.ResourceBase')),
                ('config_name', models.CharField(unique=True, max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('procedure_id', models.CharField(max_length=64)),
                ('offering_id', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=256)),
                ('start_time', models.CharField(max_length=32)),
                ('end_time', models.CharField(max_length=32)),
                ('user_start_time', models.DateTimeField()),
                ('user_end_time', models.DateTimeField()),
                ('observable_props', models.CharField(max_length=512)),
                ('selected_observable_props', models.CharField(max_length=512, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.resourcebase',),
        ),
        migrations.CreateModel(
            name='SensorServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=512)),
            ],
        ),
        migrations.AddField(
            model_name='sensor',
            name='server',
            field=models.ForeignKey(to='geonode_opensensorhub.SensorServer'),
        ),
        migrations.AddField(
            model_name='mapsensor',
            name='sensor',
            field=models.ForeignKey(to='geonode_opensensorhub.Sensor'),
        ),
    ]
