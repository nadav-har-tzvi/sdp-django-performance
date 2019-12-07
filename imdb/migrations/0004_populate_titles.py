# Generated by Django 2.2.4 on 2019-08-17 04:59
import csv
import os

import progressbar
from django.conf import settings
from django.db import migrations


DB_BATCH_SIZE = 500000


def populate_titles(apps, *args, **kwargs):
    print("Populating titles")
    Title = apps.get_model('imdb', 'Title')
    Genre = apps.get_model('imdb', 'Genre')
    TitleGenre = apps.get_model('imdb', 'TitleGenre')
    genres_by_name = {g.name: g for g in Genre.objects.all()}
    titles = []
    genres_by_titles = {}
    with open(os.path.join(settings.IMDB_DATASET_LOCATION, 'title.basics.tsv')) as f:
        reader = csv.DictReader(f, delimiter='\t')
        bar = progressbar.progressbar(reader)
        for row in bar:
            try:
                genres = [g.strip() for g in row.pop('genres').split(',') if g.strip() != '\\N']
            except:
                print(row)
                raise
            tconst = int(row.pop('tconst').strip('tt'))
            row['start_year'] = row['start_year'] if row['start_year'] != '\\N' else None
            row['end_year'] = row['end_year'] if row['end_year'] != '\\N' else None
            row['runtime_minutes'] = row['runtime_minutes'] if row['runtime_minutes'] != '\\N' else None
            title = Title(tconst=tconst, **row)
            titles.append(title)
            genres_by_titles.setdefault(tconst, [])
            for genre in genres:
                genres_by_titles[tconst].append(genres_by_name[genre])


            if len(titles) == DB_BATCH_SIZE:
                Title.objects.bulk_create(titles)
                batch_titles = Title.objects.filter(tconst__in=genres_by_titles.keys())
                titles_genres = []
                for title in batch_titles:
                    title_genres = genres_by_titles[title.tconst]
                    titles_genres.extend(
                        TitleGenre(genre=genre, title=title)
                        for genre in title_genres
                    )
                TitleGenre.objects.bulk_create(titles_genres)
                genres_by_titles.clear()
                titles_genres.clear()
                titles.clear()
        else:
            Title.objects.bulk_create(titles)
            batch_titles = Title.objects.filter(tconst__in=genres_by_titles.keys())
            titles_genres = []
            for title in batch_titles:
                title_genres = genres_by_titles[title.tconst]
                titles_genres.extend(
                    TitleGenre(genre=genre, title=title)
                    for genre in title_genres
                )
            TitleGenre.objects.bulk_create(titles_genres)
            genres_by_titles.clear()
            titles_genres.clear()
            titles.clear()

def truncate_titles(apps, *args, **kwargs):
    Title = apps.get_model('imdb', 'Title')
    Title.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('imdb', '0003_populate_crew'),
    ]

    operations = [
        migrations.RunPython(populate_titles, truncate_titles)
    ]
