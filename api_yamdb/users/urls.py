from django.urls import include, path
from rest_framework import routers

from users.views import SignupAndTokenViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('auth', SignupAndTokenViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]
