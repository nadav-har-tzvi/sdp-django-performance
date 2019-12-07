import os
import random
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import DataError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('num_users', type=int, help='Number of users to create')


    def handle(self, *args, **options):
        num_users = options['num_users']
        User = get_user_model()
        this_dir = os.path.dirname(__file__)
        with open(f'{this_dir}/names.txt') as f:
            names = f.readlines()
        for _ in range(num_users):
            name_exists = True
            while name_exists:
                name = random.choice(names)
                name_exists = User.objects.filter(username=name).exists()
            try:
                u = User(username=name)
                u.save()
            except DataError:
                print(f"Ignored name: {name} -- Too long")

