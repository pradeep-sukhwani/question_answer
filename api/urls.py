from django.conf.urls import url
from api.views import UserRegistrationViewSet, UserLoginViewSet, UserLogoutViewSet, PageViewSet, QuestionViewSet, \
    ProfileViewSet, AnswerViewSet

urlpatterns = [
    url('^sign-up/$', UserRegistrationViewSet.as_view(), name='sign-up'),
    url('^login/$', UserLoginViewSet.as_view(), name='user-login'),
    url('^logout/$', UserLogoutViewSet.as_view(), name='user-logout'),
    url('^question/$', QuestionViewSet.as_view(), name='question'),
    url('^profile/$', ProfileViewSet.as_view(), name='profile'),
    url('^answer/$', AnswerViewSet.as_view(), name='answer'),
    url('^$', PageViewSet.as_view(), name='page'),
]
