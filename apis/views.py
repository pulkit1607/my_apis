# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.views.generic import TemplateView
from rest_framework import generics, schemas

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_401_UNAUTHORIZED
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.shortcuts import render
from apis.models import Category
from .serializers import CategorySerializer


# Create your views here.
class CategoryView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)