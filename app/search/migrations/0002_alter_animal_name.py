# Generated by Django 3.2.4 on 2021-06-24 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='name',
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]