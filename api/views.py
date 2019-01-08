# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from django.contrib.auth import get_user_model, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login
from rest_framework.viewsets import ModelViewSet

from api.serializers import ProfileSerializer, UserRegistrationSerializer, UserLoginSerializer, QuestionSerializer
from core.models import Profile, Question

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

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(username=serializer.validated_data.get('user_username'))
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

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(id=serializer.validated_data.get('user_id'))
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

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            kwargs.update({'user': Profile.objects.get(user=self.request.user)})
        kwargs.update({'questions': Question.objects.all()})
        return kwargs

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        if self.request.GET.get('addNQ'):
            self.template_name = 'add_new_question.html'
        if self.request.GET.get('login-signup'):
            self.template_name = 'login_registration.html'
        else:
            self.template_name = 'home.html'
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
    permission_classes = (IsAuthenticated, )
    queryset = Question.objects.all()

    def post(self, request, format=None):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        instance = self.queryset.get(id=request.data.get('id'))
        serializer = QuestionSerializer(instance=instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
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
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        data = request.data
        data.update({'user': request.user})
        serializer = ProfileSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        instance = self.queryset.get(id=request.data.get('id'))
        serializer = ProfileSerializer(instance=instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
