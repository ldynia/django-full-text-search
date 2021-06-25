from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.postgres.search import SearchVectorField


class Animal(models.Model):
    name = models.CharField(db_index=True, max_length=64)
    url = models.CharField(max_length=1024)
    description = models.TextField()
    description_tsv = SearchVectorField(null=True)


class Artist(models.Model):
    name = models.CharField(max_length=128)
    gender = models.CharField(max_length=8)
    nationality = models.CharField(max_length=32)
    birth_year = models.PositiveIntegerField(null=True, validators=[MaxValueValidator(9999)])
    death_year = models.PositiveIntegerField(null=True, validators=[MaxValueValidator(9999)])
