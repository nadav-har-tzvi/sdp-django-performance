from django import db
from django.core.management import BaseCommand
from django.db.models import Case, When, Q

from imdb.models import WatchedTitle


class Command(BaseCommand):

    def handle(self, *args, **options):
        WatchedTitle.objects.all().update(score_class=Case(
            When(Q(score__gte=1) | Q(score__lte=3), then=0),
            When(Q(score__gte=4) | Q(score__lte=6), then=1),
            When(score__gte=7, then=2)
        ))
        sum_time = 0
        num_queries = 0
        for query in db.connections['default'].queries:
            print(query, query['time'])
            sum_time += float(query['time'])
            num_queries += 1
        print(f'Time taken to run command: {sum_time}s, number of queries: {num_queries}')