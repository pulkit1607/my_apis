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

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from rest_framework.status import HTTP_401_UNAUTHORIZED

from django.shortcuts import render
from apis.models import Category, Hotel, Menu
from .serializers import CategorySerializer, HotelResultsSerializer, MenuSerializer
import json


# Create your views here.

class CategoryView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

class ResultsView(GenericAPIView):
    api_docs = {
        'get': {
            'fields': [
                {
                    'name': 'lat',
                    'required': True,
                    'description': 'latitude of the place',
                    'type': 'number',
                    'paramType': 'query'

                },
                {
                    'name': 'long',
                    'required': True,
                    'description': 'longitude of the place',
                    'type': 'number',
                    'paramType': 'query'
                }
            ]
        }
    }

    def get(self,request, pk, *args, **kwargs):
        # lat = 28.500981
        # lng = 77.0785523

        if not self.request.GET:
            return Response({"error": "Lat & Long Required"}, status=status.HTTP_400_BAD_REQUEST,
                            content_type="application/json")

        else:
            lat = self.request.GET.get("lat")
            lng = self.request.GET.get("long")

            # if lat or lng == None:
            #     print "Inside If:"
            #     return Response({"error": "Lat & Long Required"}, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

            lat = float(lat)
            lng = float(lng)

            radius = 10
            point = Point(lng, lat)
            new_list = []
            list = Hotel.objects.filter(location__distance_lt=(point, Distance(km=radius)))

            for each in list:
                if Menu.objects.filter(hotel=each, category=pk):
                    new_list.append(each)

            print "The list is :", new_list
            serializer = HotelResultsSerializer(new_list, many=True)
            # return Response(data=lsit_1, status=status.HTTP_200_OK, content_type="application/json")
            return Response(serializer.data)

class HotelMenuView(GenericAPIView):
    # api_docs = {
    #     'get': {
    #         'fields': [
    #             {
    #                 'name': 'pk',
    #                 'required': True,
    #                 'description': 'pk of hotel',
    #                 'type': 'int',
    #
    #             }
    #         ]
    #     }
    # }

    def get_object(self, pk):
        try:
            return Hotel.objects.get(pk=pk)
        except Hotel.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        hotel = self.get_object(pk)
        print "The hotel is:", hotel
        menu = Menu.objects.filter(hotel=hotel)
        print "The Menu is:", menu
        serializer = MenuSerializer(menu, many=True)
        return Response(serializer.data)