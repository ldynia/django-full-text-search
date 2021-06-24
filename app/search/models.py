from django.db import models
from django.core.validators import MaxValueValidator


class Animal(models.Model):
  name = models.CharField(db_index=True, max_length=64)
  wiki_url = models.CharField(max_length=1024)
  description = models.TextField()


class Artist(models.Model):
  name = models.CharField(max_length=128)
  gender = models.CharField(max_length=8)
  nationality = models.CharField(max_length=32)
  birth_year = models.PositiveIntegerField(null=True, validators=[MaxValueValidator(9999)])
  death_year = models.PositiveIntegerField(null=True, validators=[MaxValueValidator(9999)])
