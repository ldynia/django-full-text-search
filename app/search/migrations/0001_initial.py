# Generated by Django 3.2.4 on 2021-06-25 13:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('url', models.CharField(max_length=1024)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('gender', models.CharField(max_length=8)),
                ('nationality', models.CharField(max_length=32)),
                ('birth_year', models.PositiveIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999)])),
                ('death_year', models.PositiveIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999)])),
            ],
        ),
    ]
