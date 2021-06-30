from django.contrib.postgres.search import SearchQuery
from django.contrib.postgres.search import SearchRank
from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand
from django.db import connection

from search.models import Animal
from search.utils import CoalesceLessSearchVector
from search.utils import VectorLessSearch


class Command(BaseCommand):

    help = 'Benchmark ORM'

    def handle(self, *args, **options):
        self.__bench_description_annotate_search()
        self.__bench_description_tsv_annotate_search()
        self.__bench_description_filter_search()
        self.__bench_description_tsv_filter_search()
        self.__bench_rank_search()

    def __bench_rank_search(self):
        # Fast
        animals = Animal.objects.annotate(rank=SearchRank(VectorLessSearch('description_tsv'), SearchQuery('cat & stripes', config='english', search_type='raw'))).order_by('-rank')
        print(animals)
        print('Time:', connection.queries[-1]['time'], 'ms')
        print('Query:', connection.queries[-1]['sql'])

        # Slow
        animals = Animal.objects.annotate(rank=SearchRank(CoalesceLessSearchVector('description', config='english'), SearchQuery('cat & stripes', config='english', search_type='raw'))).order_by('-rank')
        print()
        print(animals)
        print('Time:', connection.queries[-1]['time'], 'ms')
        print('Query:', connection.queries[-1]['sql'])


    def __bench_description_annotate_search(self):
        # INFO: Slow
        animals = Animal.objects.annotate(search=SearchVector('description', config='english')).filter(search='cats')
        print(animals)
        print('Time:', connection.queries[-1]['time'], 'ms')
        print('Query:', connection.queries[-1]['sql'])

        # INFO: Fast
        animals = Animal.objects.annotate(search=CoalesceLessSearchVector('description', config='english')).filter(search=SearchQuery('cats', config='english', search_type='raw'))
        print()
        print(animals)
        print('Time:', connection.queries[-1]['time'], 'ms')
        print('Query:', connection.queries[-1]['sql'])


    def __bench_description_tsv_annotate_search(self):
        # INFO: Fast
        animals = Animal.objects.annotate(search=VectorLessSearch('description_tsv')).filter(search=SearchQuery('cats & stripes', config='english', search_type='raw'))
        print(animals)
        print('Time:', connection.queries[-1]['time'], 'ms')
        print('Query:', connection.queries[-1]['sql'])


    def __bench_description_filter_search(self):
        # INFO: Fast
        animals = Animal.objects.filter(description__search=SearchQuery('stripes | cat', config='english', search_type='raw'))
        print()
        print(animals)
        print('Time:', connection.queries[-1]['time'], 'ms')
        print('Query:', connection.queries[-1]['sql'])


    def __bench_description_tsv_filter_search(self):
        # INFO: Fast
        animals = Animal.objects.filter(description_tsv=SearchQuery('cat | stripes', config='english', search_type='raw'))
        print(animals)
        print('Time:', connection.queries[-1]['time'], 'ms')
        print('Query:', connection.queries[-1]['sql'])

