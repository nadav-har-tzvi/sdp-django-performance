# Generated by Django 2.2.4 on 2019-08-24 13:40
import csv
import os

import progressbar
from django.conf import settings
from django.db import migrations

DB_BATCH_SIZE = 500000


def populate_episodes(apps, *args, **kwargs):
    print("Populating title episodes")
    Title = apps.get_model('imdb', 'Title')
    TitleEpisode = apps.get_model('imdb', 'TitleEpisode')

    num_scanned = 0
    with open(os.path.join(settings.IMDB_DATASET_LOCATION, 'title.episode.tsv')) as f:
        reader = csv.DictReader(f, delimiter='\t')
        bar = progressbar.progressbar(reader)
        title_episodes = []
        titles = set()
        parent_titles = set()
        for row in bar:
            row['tconst'] = tconst = int(row['tconst'].strip('tt'))
            row['parentTconst'] = parent_tconst = int(row['parentTconst'].strip('tt'))
            row['seasonNumber'] = row['seasonNumber'] if row['seasonNumber'] != '\\N' else None
            row['episodeNumber'] = row['episodeNumber'] if row['episodeNumber'] != '\\N' else None
            title_episodes.append(row)
            parent_titles.add(parent_tconst)
            titles.add(tconst)
            num_scanned += 1
            if num_scanned == DB_BATCH_SIZE:
                title_by_tconst = {t.tconst: t for t in Title.objects.filter(tconst__in=titles)}
                parents_by_tconst = {t.tconst: t for t in Title.objects.filter(tconst__in=parent_titles)}
                title_episodes_batch = []
                for title_episode in title_episodes:
                    tconst = title_episode['tconst']
                    parent_tconst = title_episode['parentTconst']
                    try:
                        title_episodes_batch.append(TitleEpisode(
                            episode_title=title_by_tconst[tconst],
                            series_title=parents_by_tconst[parent_tconst],
                            season_number=title_episode['seasonNumber'],
                            episode_number=title_episode['episodeNumber']
                        ))
                    except KeyError:
                        pass
                TitleEpisode.objects.bulk_create(title_episodes_batch)
                title_episodes_batch.clear()
                parent_titles.clear()
                titles.clear()
                title_episodes.clear()
                num_scanned = 0
        else:
            TitleEpisode.objects.bulk_create(title_episodes_batch)
            title_episodes_batch.clear()
            parent_titles.clear()
            titles.clear()
            title_episodes.clear()

def truncate_episodes(apps, *args, **kwargs):
    TitleEpidoe = apps.get_model('imdb', 'TitleEpisode')
    TitleEpidoe.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('imdb', '0005_populate_title_crews'),
    ]

    operations = [
        migrations.RunPython(populate_episodes, truncate_episodes)
    ]
