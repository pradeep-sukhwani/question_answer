from django.conf.urls import url
from api.views import UserRegistrationViewSet, UserLoginViewSet, UserLogoutViewSet, HomePageViewSet

urlpatterns = [
    url('sign-up/', UserRegistrationViewSet.as_view(), name='sign-up'),
    url('login/', UserLoginViewSet.as_view(), name='user-login'),
    url('logout/', UserLogoutViewSet.as_view(), name='user-logout'),
    url('', HomePageViewSet.as_view(), name='profile'),
]
