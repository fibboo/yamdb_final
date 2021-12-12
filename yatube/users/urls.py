from django.urls import path

from users.views import SingUp


urlpatterns = [
    path('signup/', SingUp.as_view(), name='signup')
]
