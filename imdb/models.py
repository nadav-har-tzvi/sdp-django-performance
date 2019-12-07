from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models


class Genre(models.Model):

    name = models.CharField(max_length=32)


class Profession(models.Model):

    name = models.CharField(max_length=128)


class CrewMemberProfession(models.Model):
    member = models.ForeignKey('CrewMember', on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)


class CrewMember(models.Model):
    nconst = models.IntegerField(db_index=True)
    primary_name = models.CharField(max_length=105)
    birth_year = models.IntegerField(null=True)
    death_year = models.IntegerField(null=True)
    professions = models.ManyToManyField(Profession, related_name='crew_members', through=CrewMemberProfession)


class TitleCrew(models.Model):
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    member = models.ForeignKey('CrewMember', on_delete=models.CASCADE)
    ordering = models.IntegerField()
    category = models.ForeignKey('Profession', on_delete=models.CASCADE)
    characters = models.TextField()


class Title(models.Model):
    tconst = models.IntegerField(db_index=True)
    title_type = models.CharField(max_length=32)
    primary_title = models.CharField(max_length=512)
    original_title = models.CharField(max_length=512)
    is_adult = models.BooleanField(default=False)
    start_year = models.IntegerField(null=True)
    end_year = models.IntegerField(null=True)
    runtime_minutes = models.IntegerField(null=True)
    genres = models.ManyToManyField(Genre, through='TitleGenre', related_name='titles')
    crew = models.ManyToManyField(CrewMember, through='TitleCrew', related_name='titles')
    episodes = models.ManyToManyField('Title', through='TitleEpisode')


    @property
    def directors(self):
        return self.titlecrew_set.filter(category__name='director')

    @property
    def actors(self):
        return self.titlecrew_set.filter(category__name__in=['actor', 'actress', 'self'])


class TitleGenre(models.Model):

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)


class AlternativeTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='alternative_titles')
    ordering = models.IntegerField()
    alternative_title = models.CharField(max_length=512)
    region = models.CharField(max_length=2)
    language = models.CharField(max_length=2)
    types = models.CharField(max_length=16)
    attributes = models.CharField(max_length=16)
    is_original_title = models.BooleanField(default=False)


class TitleRating(models.Model):

    title = models.OneToOneField(Title, on_delete=models.CASCADE, related_name='rating')
    average_rating = models.FloatField()
    num_votes = models.IntegerField()


class TitleEpisode(models.Model):
    parent_tconst = models.CharField(max_length=16)
    season_number = models.IntegerField(null=True)
    episode_number = models.IntegerField(null=True)
    episode_title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='series_in')
    series_title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='episodes_of')


class WatchedTitle(models.Model):

    SCORE_CLASSES = (
        (0, 'Bad'),
        (1, 'Neutral'),
        (2, 'Good')
    )

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    score = models.IntegerField(validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10)])
    score_class = models.IntegerField(choices=SCORE_CLASSES, null=True)