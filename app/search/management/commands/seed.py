import requests

from django.core.management.base import BaseCommand

from search.models import Animal
from search.models import Artist
from .data.animals import COMMON_ANIMALS


class Command(BaseCommand):

    help = 'Seed database'

    def handle(self, *args, **options):
      self.__seed_animals()
      self.__seed_artists()


    def __seed_animals(self):
      print('Start saving animal data')

      for animal in COMMON_ANIMALS:
        if not Animal.objects.filter(name=animal):
          url = f'https://en.wikipedia.org/w/api.php?action=query&titles={animal}&prop=extracts&exlimit=1&explaintext=1&formatversion=2&format=json'
          r = requests.get(url)
          description = r.json()['query']['pages'][0]['extract']
          if r.status_code == 200 and description:
            Animal(name=animal, url=url, description=description).save()

      print('Done saving animal  data')


    def __seed_artists(self):
      print('Start saving artist data')
      with open('/app/search/management/commands/data/artists.csv') as file:
        artists = []
        for line in file.readlines()[1:]:
          artist_data = line.rstrip().split(',')
          artists.append(Artist(
            name=artist_data[0],
            gender=artist_data[1],
            nationality=artist_data[2],
            birth_year=int(artist_data[3]) if artist_data[3] else None,
            death_year=int(artist_data[4]) if artist_data[4] else None,
          ))
        Artist.objects.bulk_create(artists)
      print('Done saving artist data')
