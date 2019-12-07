import random
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.models import Max, Min

from imdb.models import Title, WatchedTitle


class Command(BaseCommand):

    def handle(self, *args, **options):
        User = get_user_model()
        agg = Title.objects.aggregate(max_id=Max('id'), min_id=Min('id'))
        min_id = agg['min_id']
        max_id = agg['max_id']
        watched_titles = []
        for user in User.objects.all():
            print(user)
            for choice in random.choices(range(min_id, max_id), k=100):
                title = Title.objects.get(pk=choice)
                wt = WatchedTitle(user=user, title=title, score=random.randint(1, 10))
                watched_titles.append(wt)
        WatchedTitle.objects.bulk_create(watched_titles)