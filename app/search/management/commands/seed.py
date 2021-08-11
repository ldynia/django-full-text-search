import random
import requests
import uuid

from django.core.management.base import BaseCommand

from search.models import Animal
from search.models import Artist
from .data.animals import COMMON_ANIMALS


class Command(BaseCommand):

    help = 'Seed database'

    def handle(self, *args, **options):
        self.__seed_artists()
        self.__seed_animals()
        self.__seed_big_animals()

    def __seed_big_animals(self):
        BATCH_SIZE = 1000
        MAX_RECORDS = 10000
        for step in range(0, MAX_RECORDS, BATCH_SIZE):
            print("Seeding", step + BATCH_SIZE, "records from", MAX_RECORDS, "records")
            animals_batch = self.__gen_animal(BATCH_SIZE)
            Animal.objects.bulk_create(animals_batch, BATCH_SIZE)

    def __seed_animals(self):
      print('Start saving animal data')

      for animal in COMMON_ANIMALS:
        if not Animal.objects.filter(name=animal):
          url = f'https://en.wikipedia.org/w/api.php?action=query&titles={animal}&prop=extracts&exlimit=1&explaintext=1&formatversion=2&format=json'
          r = requests.get(url)
          description = r.json()['query']['pages'][0]['extract']
          if r.status_code == 200 and description:
            Animal(name=animal, url=url, description=description, meta_json={"name": animal, "description": description}).save()

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

    def __gen_animal(self, size):
        animals = []
        for _ in range(size):
            animal = random.choice(COMMON_ANIMALS)
            animal = Animal.objects.filter(name=animal).first()
            if animal:
                description_list = animal.description.split()
                random.shuffle(description_list)
                description = ' '.join(description_list)
                animals.append(Animal(name=str(uuid.uuid4()), url=animal.url, description=description))
        return animals
