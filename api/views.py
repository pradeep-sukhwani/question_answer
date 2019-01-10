# -*- coding: utf-8 -*-
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import status
from django.contrib.auth import get_user_model, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login
from api.serializers import ProfileSerializer, UserRegistrationSerializer, UserLoginSerializer, QuestionSerializer,\
    AnswerSerializer
from core.models import Profile, Question, Answer, Tag

User = get_user_model()


class UserRegistrationViewSet(APIView):
    """
        Creates the user.
        Model:
            User

        :returns:
            Token key
            Email address
            user id
    """
    serializer_class = UserRegistrationSerializer
    querset = User.objects.filter(is_active=True)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = self.querset.objects.get(username=serializer.validated_data.get('user_username'))
            login(request, user)
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginViewSet(APIView):
    """
        Login the user.
        Model:
            User

        :returns:
            Token key
            username
            user id
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserLoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = self.queryset.get(id=serializer.validated_data.get('user_id'))
            login(request, user)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutViewSet(APIView):
    """
        Logout the user.
    """

    def get(self, request, format=None):
        logout(request)
        return HttpResponseRedirect(redirect_to=reverse("api:page"))


class PageViewSet(TemplateView):
    """
    This viewset is for the homepage. It checks whether the user is logged or not
    and based on that it selects the template
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        question = Question.objects.all()
        data = {'tags': Tag.objects.all(), 'questions': question}
        if self.request.GET.get('search_text'):
            data.update({'questions': question.filter(Q(title__icontains=self.request.GET.get('search_text')) |
                                                      Q(tag__in=data['tags'].filter(name__icontains=self.request.GET.get('search_text')))).distinct()
                         })
        if self.request.GET.get('question_thread_id'):
            try:
                answer = Answer.objects.get(accepted_or_not=True,
                                            question_answer__id=self.request.GET.get('question_thread_id'))
            except Answer.DoesNotExist:
                answer = None
            data.update({'question': question.get(id=self.request.GET.get('question_thread_id')),
                         'accepted': answer})
            self.template_name = 'question_answer_thread.html'
        if self.request.GET.get('question_id'):
            self.template_name = 'question.html'
            data.update({'question': Question.objects.get(id=self.request.GET.get('question_id'))})
        if self.request.GET.get('question_id'):
            self.template_name = 'question.html'
            data.update({'question': Question.objects.get(id=self.request.GET.get('question_id'))})
        if self.request.GET.get('question'):
            self.template_name = 'question.html'
        if self.request.user.is_authenticated:
            if self.request.GET.get('profile'):
                self.template_name = 'profile.html'
            profile = Profile.objects.filter(user=self.request.user)
            if profile:
                profile = profile.first()
                data.update({'user': profile, 'user_question': question.filter(asked_by=profile),
                             'user_answer': Answer.objects.filter(answer_by=profile)})
        else:
            if self.request.GET.get('login-signup'):
                self.template_name = 'login_registration.html'
        kwargs.update(data)
        return kwargs

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=self.get_context_data(),
            using=self.template_engine,
            **response_kwargs
        )


class QuestionViewSet(APIView):
    """
    This view set is for to add a new question or edit an existing question
    """
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=serializer.validated_data.get('status'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnswerViewSet(APIView):
    """
    This viewset will let user to do create,
    update profile

    Models:
    Profile
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def post(self, request, format=None):
        data = request.data.dict()
        data.update({'user': request.user})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=serializer.validated_data.get('status'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(APIView):
    """
    This viewset will let user to do create,
    update profile

    Models:
    Profile
    """
    queryset = Profile.objects.filter(user__is_active=True)
    serializer_class = ProfileSerializer

    def post(self, request, format=None):
        data = request.data.dict()
        data.update({'user': request.user})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=serializer.validated_data.get('status'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
