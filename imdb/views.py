from collections import defaultdict

from django.db.models import Avg, Count, Prefetch
from django.http import Http404
from django.views import generic
from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import viewsets, filters, pagination

# Create your views here.
from imdb.models import Title, TitleCrew, TitleGenre, Genre, TitleEpisode, Profession, CrewMember
from imdb.serializers import TitleSerializer


class HomeView(generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data()
        context['top_movies'] = Title.objects.order_by('-rating__average_rating')[:10]
        context['popular_movies'] = Title.objects.order_by('-rating__num_votes')[:10]
        # context['new_movies'] = Title.objects.order_by('-start_year')[:20]

    def _get_top_actors_naive(self):
        """
        Unoptimized as F
        Steer clear
        DANGER!
        365 seconds runtime.
        Hundreds of SQL Queries
        HALP!
        :return:
        """
        num_movies_per_actor = defaultdict(int)
        for actor in TitleCrew.objects.filter(category__name__in=['actor', 'actress']):
            num_movies_per_actor[actor.id] += 1
        actors_with_more_than_one_title = [actor for actor in TitleCrew.objects.filter(category__name__in=['actor', 'actress']) if num_movies_per_actor[actor.id] > 1]
        avg_score_per_actor = defaultdict(float)
        for actor in actors_with_more_than_one_title:
            agg_score = 0
            for title in actor.titles.all():
                agg_score += title.rating.average_rating
            avg_score_per_actor[actor.id] = agg_score / actor.titles.count()
        actors_sotred_by_score = sorted(avg_score_per_actor.items(), key=lambda t: t[1])
        actors_sotred_by_score.reverse()
        top_actors = [t[0] for t in actors_sotred_by_score[:10]]
        return top_actors

    def _get_top_actors_somewhat_faster(self):
        """
        order_by invokes full table scan. BAD!
        ~ 73 seconds runtime.
        Not as bad.
        Still objectively bad.
        :return:
        """
        return list(TitleCrew.objects.filter(category__name__in=['actor', 'actress']).values(
            'member').annotate(
            num_movies=Count('title_id')).filter(num_movies__gt=1).annotate(
            score=Avg('title__rating__average_rating')).values('member', 'score').order_by('-score')[:10])

    def _get_top_actors_even_better(self):
        """
        ~ 60 seconds
        Not amazing
        :return:
        """
        qs = TitleCrew.objects.filter(category__name__in=['actor', 'actress']).values(
            'member').annotate(
            num_movies=Count('title_id')).filter(num_movies__gt=1).annotate(
            score=Avg('title__rating__average_rating')).values('member', 'score').exclude(score__isnull=True)
        print(qs.query)
        members_with_scores = list(qs)
        members_with_scores.sort(key=lambda x: -x['score'])
        return members_with_scores[:10]

    def _get_top_actors_cached(self):
        """
        ~ 60 seconds for the first time
        Milliseconds in the subsequent times
        :return:
        """
        actors = cache.get('top_actors')
        if actors:
            cache.touch('top_actors', 3600)
        else:
            actors = self._get_top_actors_even_better()
            cache.set('top_actors', actors, 3600)
        return actors


    def dispatch(self, request, *args, **kwargs):

        return super().dispatch(request, *args, **kwargs)

class TitlesListView(generic.ListView):

    model = Title
    queryset = Title.objects.exclude(title_type='tvEpisode')
    paginate_by = 1000
    template_name = 'movies.html'
    context_object_name = 'movies'
    ordering = 'start_year'
    page_kwarg = 'cursor'

    def get_naive_queryset(self):
        return Title.objects.exclude(title_type='tvEpisode')

    def get_queryset_with_eager_genres_and_episodes(self):
        return Title.objects.exclude(title_type='tvEpisode').prefetch_related('genres', 'episodes')

    def get_queryset_with_eager_crew(self):  # Good, but not good enough, we also need the profession!
        return Title.objects.exclude(title_type='tvEpisode').prefetch_related('genres', 'episodes', 'crew')

    def get_queryset_with_eager_crew_and_professions(self):
        # tv_type = TitleType.objects.get(name='tvEpisode')
        return Title.objects.exclude(title_type='tvEpisode').prefetch_related(
            'genres',
            'episodes',
            Prefetch('titlecrew_set', TitleCrew.objects.filter(category__name='director')
                     .select_related('category')
                     .select_related('member'), to_attr='directors'),
            Prefetch('titlecrew_set', TitleCrew.objects.filter(category__name__in=['actor', 'actress', 'self'])
                     .select_related('category')
                     .select_related('member'), to_attr='actors')
        )

    # def paginate_queryset(self, queryset, page_size):
    #     paginator = CursorPaginator(queryset, ordering=(self.ordering, 'id'))
    #     page_kwarg = self.page_kwarg
    #     cursor = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg)
    #     direction = self.kwargs.get('direction') or self.request.GET.get('direction') or 'after'
    #     try:
    #         page = paginator.page(page_size, **{direction: cursor})
    #         return (paginator, page, page.items, page.has_next)
    #     except InvalidCursor as e:
    #         raise Http404(_('Invalid cursor (%(cursor)s)') % {
    #             'cursor': cursor
    #         })

    # def get _queryset(self):
    #     return self.get_naive_queryset()
        # qs = self.get_queryset_using_fk()
        # qs = self.get_queryset_with_eager_genres_and_episodes()
        # qs = self.get_queryset_with_eager_crew()
        # qs = self.get_queryset_with_eager_crew_and_professions()
        # ordering = self.get_ordering()
        # if ordering:
        #     if isinstance(ordering, str):
        #         ordering = (ordering,)
        #     qs = qs.order_by(*ordering)
        #
        # return qs

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(object_list=object_list, **kwargs)
    #     paginator = context['paginator']
    #     page = context['page_obj']
    #     context['next_cursor'] = paginator.cursor(page[-1])
    #     context['prev_cursor'] = paginator.cursor(page[0])
    #     return context


class TitlesCursorPaginator(pagination.CursorPagination):

    page_size = 1000

class TitlesPageNumberPaginator(pagination.PageNumberPagination):

    page_size = 1000
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class TitlesListViewSet(viewsets.ReadOnlyModelViewSet):

    filter_backends = [filters.OrderingFilter]

    ordering_fields = ['id']
    ordering = ['start_year', 'id']
    serializer_class = TitleSerializer
    pagination_class = TitlesCursorPaginator

    def _get_episodes_by_series(self, title_ids):
        episodes_by_title = defaultdict(list)
        for episode in TitleEpisode.objects.filter(series_title_id__in=title_ids).values():
            # episodes_by_title.setdefault(episode['series_title_id'], [])
            episodes_by_title[episode['series_title_id']].append(episode)
        return episodes_by_title

    def _get_directors_by_title(self, title_ids):
        director_prof = Profession.objects.get(name='director')
        member_ids = TitleCrew.objects.filter(category=director_prof, title_id__in=title_ids).values_list('member_id', flat=True)
        members = {m['id']: m for m in CrewMember.objects.filter(id__in=member_ids).values()}
        directors_by_title = defaultdict(list)
        for tc in TitleCrew.objects.filter(category=director_prof, title_id__in=title_ids).values():
            directors_by_title[tc['title_id']].append(members[tc['member_id']])
        return directors_by_title

    def _get_actors_by_title(self, title_ids):
        actor_profs = Profession.objects.filter(name__in=['actor', 'actress', 'self'])
        member_ids = TitleCrew.objects.filter(category__in=actor_profs, title_id__in=title_ids).values_list('member_id', flat=True)
        members = {m['id']: m for m in CrewMember.objects.filter(id__in=member_ids).values()}
        actors_by_title = defaultdict(list)
        for tc in TitleCrew.objects.filter(category__in=actor_profs, title_id__in=title_ids).values():
            actors_by_title[tc['title_id']].append(members[tc['member_id']])
        return actors_by_title

    def _get_genres_by_titles(self, title_ids):
        genres_by_id = {g['id']: g for g in Genre.objects.values()}
        title_genres = {t['title_id']: genres_by_id[t['genre_id']] for t in
                        TitleGenre.objects.filter(title_id__in=title_ids).values('title_id', 'genre_id')}
        return title_genres

    # def get_serializer_context(self):
    #     context = super(TitlesListViewSet, self).get_serializer_context()
    #     page = self.paginate_queryset(self.queryset)
    #     title_ids = [t['id'] for t in page]
    #     context['title_genres'] = self._get_genres_by_titles(title_ids)
    #     context['title_episodes'] = self._get_episodes_by_series(title_ids)
    #     context['title_directors'] = self._get_directors_by_title(title_ids)
    #     context['title_actors'] = self._get_actors_by_title(title_ids)
    #     return context




    def get_queryset(self):
        return Title.objects.exclude(title_type='tvEpisode')\
                            .only('primary_title', 'start_year', 'genres')\
                            .prefetch_related(
                            'genres',
                            'episodes',
                            Prefetch('titlecrew_set', TitleCrew.objects.filter(category__name='director')
                                     .select_related('category')
                                     .prefetch_related(Prefetch('member', CrewMember.objects.only('primary_name'))), to_attr='directors'),
                            Prefetch('titlecrew_set', TitleCrew.objects.filter(category__name__in=['actor', 'actress', 'self'])
                                     .select_related('category')
                                     .prefetch_related(
                                Prefetch('member', CrewMember.objects.defer('nconst', 'birth_year', 'death_year', 'professions'))),
                                     to_attr='actors')
        )