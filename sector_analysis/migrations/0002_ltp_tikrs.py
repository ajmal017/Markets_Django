# Generated by Django 3.0.4 on 2020-11-22 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sector_analysis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ltp_tikrs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tikr', models.CharField(max_length=64)),
                ('ltp', models.FloatField()),
            ],
        ),
    ]
