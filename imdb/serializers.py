from rest_framework import serializers

from imdb.models import Title


class TitleSerializer(serializers.ModelSerializer):

    genres = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)
    directors = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()


    class Meta:
        model = Title
        fields = ['id', 'primary_title', 'start_year', 'genres', 'directors', 'actors']

    # def get_genres(self, title):
    #     return self.context['title_genres'][title['id']]


    def get_directors(self, title):
        return [director.member.primary_name for director in title.directors]

    def get_actors(self, title):
        return [actor.member.primary_name for actor in title.actors]

    # def get_directors(self, title):
    #     directors = self.context['title_directors']
    #     return [director['primary_name'] for director in directors[title['id']]]
    #
    # def get_actors(self, title):
    #     actors = self.context['title_actors']
    #     return [actor['primary_name'] for actor in actors[title['id']]]
    #
    # def get_episodes_count(self, title):
    #     return len(self.context['title_episodes'])