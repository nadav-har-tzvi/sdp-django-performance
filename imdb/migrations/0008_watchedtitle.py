# Generated by Django 2.2.8 on 2019-12-07 15:29

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('imdb', '0007_populate_ratings'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchedTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('score_class', models.IntegerField(choices=[(0, 'Bad'), (1, 'Neutral'), (2, 'Good')], null=True)),
                ('title', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='imdb.Title')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
