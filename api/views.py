# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from django.contrib.auth import get_user_model, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login
from api.serializers import ProfileSerializer, UserRegistrationSerializer, UserLoginSerializer
from core.models import Profile
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
        return HttpResponseRedirect(redirect_to=reverse("api:profile"))


class HomePageViewSet(TemplateView):
    """
    This viewset is for the homepage. It checks whether the user is logged or not
    and based on that it selects the template
    """

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            kwargs.update({'user': Profile.objects.get(user=self.request.user)})
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
            template='dashboard.html' if self.request.user.is_authenticated else 'login_registration.html',
            context=self.get_context_data(),
            using=self.template_engine,
            **response_kwargs
        )


class ProfileViewSet(GenericAPIView):
    """
    This viewset will let user to do create,
    update profile

    Models:
    Profile
    Tags
    UserQuestion
    UserAnswer
    """
    queryset = Profile.objects.filter(user__is_active=True)
    serializer_class = ProfileSerializer
