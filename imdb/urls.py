from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('api', views.TitlesListViewSet, base_name='titles')

urlpatterns = [
    path('titles', views.TitlesListView.as_view())
]

urlpatterns = router.urls + urlpatterns