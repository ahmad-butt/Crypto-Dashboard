# Generated by Django 3.2.16 on 2023-04-07 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20230208_0604'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradePair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker1', models.CharField(max_length=20)),
                ('ticker2', models.CharField(max_length=20)),
            ],
        ),
    ]