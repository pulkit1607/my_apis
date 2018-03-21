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
from django.contrib.auth.models import User

from django.shortcuts import render
from apis.models import Category, Hotel, Menu, Profile, Cart, CartDetails
from .serializers import CategorySerializer, HotelResultsSerializer, MenuSerializer, AuthCustomTokenSerializer
from  my_apis.utils import create_username
import json


# Create your views here.

class CategoryView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

class ResultsView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

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
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Hotel.objects.get(pk=pk)
        except Hotel.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        hotel = self.get_object(pk)
        menu = Menu.objects.filter(hotel=hotel)
        serializer = MenuSerializer(menu, many=True)
        return Response(serializer.data)

class SignUpView(APIView):
    api_docs = {
        'post': {
            'fields': [
                {
                    'name': 'name',
                    'required': True,
                    'description': 'name',
                    'type': 'string',

                },
                {
                    'name': 'email',
                    'required': True,
                    'description': 'email',
                    'type': 'string',
                },
                {
                    'name': 'phone',
                    'required': True,
                    'description': 'phone',
                    'type': 'integer',
                },
                {
                    'name': 'password',
                    'required': True,
                    'description': 'password',
                    'type': 'string',
                }
            ]
        }
    }

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')

        try:
            existing_user = User.objects.get(email__iexact=email)
            if existing_user:
                content = {
                    'status': {
                        'isSuccess': False,
                        'code': "FAILURE",
                        'message': "Invalid",
                    },
                    'error': "An account already exists under this email address."
                }

                return Response(content, status.HTTP_400_BAD_REQUEST)
        except User.MultipleObjectsReturned:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Invalid",
                },
                'error': "An account already exists under this email address."
            }

            return Response(content, status.HTTP_400_BAD_REQUEST)
        except:
            pass


        user = User.objects.create_user(create_username(name),email, password)
        user.first_name = name
        user.is_active = True
        user.save()
        profile, created = Profile.objects.get_or_create(user=user)
        profile.contact = phone
        profile.complete=True
        profile.save()
        content = {
            'status': {
                'isSuccess': True,
                'code': "SUCCESS",
                'message': "Success"
            }
        }

        return Response(content, status.HTTP_200_OK)

class UserLoginView(APIView):
    api_docs = {
        'post': {
            'fields': [
                {
                    'name': 'email',
                    'required': True,
                    'description': 'Email of user',
                    'type': 'string'
                },
                {
                    'name': 'password',
                    'required': True,
                    'description': 'Password of user',
                    'type': 'string'
                },
            ]
        }
    }

    def post(self, request):
        serializer = AuthCustomTokenSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user_request = User.objects.get(email__iexact=email)
            except:
                content = {
                    'status': {
                        'isSuccess': False,
                        'code': "FAILURE",
                        'message': "Invalid Credentials",
                    },
                    'error': "Either email or password is incorrect."
                }
                return Response(content, status.HTTP_400_BAD_REQUEST)

            username = user_request.username
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    content = {
                        'status': {
                            'isSuccess': True,
                            'code': "SUCCESS",
                            'message': "Success"
                        },
                        'token': token.key,
                        'employee': serializer.data
                    }

                    return Response(content, status.HTTP_200_OK)
                else:
                    content = {
                        'status': {
                            'isSuccess': False,
                            'code': "FAILURE",
                            'message': "Permission Denied",
                        },
                        'error': "Your access to this portal is restricted by your comapny."
                    }

                    return Response(content, status.HTTP_400_BAD_REQUEST)
            else:
                content = {
                    'status': {
                        'isSuccess': False,
                        'code': "FAILURE",
                        'message': "Invalid Credentials",
                    },
                    'error': "Either email or password is incorrect."
                }

            return Response(content, status.HTTP_200_OK)
        else:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Invalid Credentials",
                },
                'error': serializer.errors
            }

            return Response(content, status.HTTP_400_BAD_REQUEST)

class AddToCartView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    api_docs = {
        'post': {
            'fields': [
                {
                    'name': 'prod_id',
                    'required': True,
                    'description': 'product id',
                    'type': 'number'
                },
                {
                    'name': 'qty',
                    'required': True,
                    'description': 'Quantity',
                    'type': 'number'
                },
            ]
        }
    }

    def post(self, request):
        user = self.request.user
        if user:
            prod = request.data.get('prod_id')
            obj = Menu.objects.filter(id=prod).first()
            qty = request.data.get('qty')
            cart, created = Cart.objects.get_or_create(customer=user)
            cart_details, created = CartDetails.objects.get_or_create(
                cart=cart,
                product=obj,
                price=obj.price,
            )
            cart_details.qty=qty
            cart_details.save()
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                }
            }
            return Response(content, status.HTTP_200_OK)
        else:

            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "User not logged in",
                }
            }

            return Response(content, status.HTTP_400_BAD_REQUEST)


