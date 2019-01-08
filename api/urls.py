from django.conf.urls import url
from api.views import UserRegistrationViewSet, UserLoginViewSet, UserLogoutViewSet, PageViewSet, QuestionViewSet

urlpatterns = [
    url('^sign-up/$', UserRegistrationViewSet.as_view(), name='sign-up'),
    url('^login/$', UserLoginViewSet.as_view(), name='user-login'),
    url('^logout/$', UserLogoutViewSet.as_view(), name='user-logout'),
    url('^question/$', QuestionViewSet.as_view(), name='question'),
    url('^$', PageViewSet.as_view(), name='page'),
]
