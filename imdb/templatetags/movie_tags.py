from django import template

from imdb.models import Title, TitleCrew

register = template.Library()


@register.filter()
def get_director(movie: Title):
    director_positions = TitleCrew.objects.filter(title=movie, category__name='director')
    return ', '.join([p.member.primary_name for p in director_positions]) or '-'


@register.filter()
def get_actors(movie: Title):
    actor_positions = TitleCrew.objects.filter(title=movie).filter(category__name__in=['actor', 'actress', 'self'])
    return ', '.join([p.member.primary_name for p in actor_positions]) or '-'
