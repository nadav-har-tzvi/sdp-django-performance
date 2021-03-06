# Generated by Django 2.2.4 on 2019-08-14 18:36

from django.db import migrations
from django.conf import settings
import pandas as pd
import os



def _populate_professions(apps):
    print("Populating professions")
    Profession = apps.get_model('imdb', 'Profession')
    professions = pd.read_csv(os.path.join(settings.IMDB_DATASET_LOCATION, 'name.basics.tsv'), sep='\t')['primaryProfession']
    professions = professions.replace('\\N', pd.np.nan).dropna().map(lambda x: x.split(','))
    unique_professions = pd.DataFrame(professions.tolist()) \
                        .stack() \
                        .reset_index(level=1, drop=True) \
                        .reset_index(name='genres')['genres'] \
                        .unique() \
                        .tolist()
    profession_objs = [Profession(name=profession) for profession in unique_professions]
    Profession.objects.bulk_create(profession_objs)


def populate_enums(apps, *args, **kwargs):
    _populate_genres(apps)
    _populate_professions(apps)


def _populate_genres(apps):
    print("Populating genres")
    Genre = apps.get_model('imdb', 'Genre')
    genres = pd.read_csv(os.path.join(settings.IMDB_DATASET_LOCATION, 'title.basics.tsv'), sep='\t')['genres']
    genres = genres.replace('\\N', pd.np.nan).dropna().map(lambda x: x.split(','))
    unique_genres = pd.DataFrame(genres.tolist()) \
        .stack() \
        .reset_index(level=1, drop=True) \
        .reset_index(name='genres')['genres'] \
        .unique() \
        .tolist()
    genre_objs = [Genre(name=genre) for genre in unique_genres]
    Genre.objects.bulk_create(genre_objs)


def truncate_enums(apps, *args, **kwargs):
    Profession = apps.get_model('imdb', 'Profession')
    TitleGenre = apps.get_model('imdb', 'TitleGenre')
    Profession.objects.all().delete()
    TitleGenre.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('imdb', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_enums, truncate_enums)
    ]
