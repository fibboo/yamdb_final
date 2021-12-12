from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(
    'categories', views.CategoryViewSet, basename='categories'
)
router.register(
    'genres', views.GenreViewSet, basename='genres'
)
router.register(
    'titles', views.TitleViewSet, basename='titles'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet, basename='reviews',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet, basename='comments',
)
urlpatterns = [
    path('v1/', include(router.urls))
]
