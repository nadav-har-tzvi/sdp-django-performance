from django import db
from django.core.management import BaseCommand

from imdb.models import WatchedTitle


class Command(BaseCommand):

    def handle(self, *args, **options):
        wts = list(WatchedTitle.objects.all())
        for wt in wts:
            if 1 <= wt.score <= 3:
                wt.score_class = 0
            elif 4 <= wt.score <= 6:
                wt.score_class = 1
            else:
                wt.score_class = 2
        WatchedTitle.objects.bulk_update(wts, ['score_class'])
        sum_time = 0
        num_queries = 0
        for query in db.connections['default'].queries:
            print(query, query['time'])
            sum_time += float(query['time'])
            num_queries += 1
        print(f'Time taken to run command: {sum_time}s, number of queries: {num_queries}')