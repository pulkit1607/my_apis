# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from braces.views import AjaxResponseMixin,JSONResponseMixin
from django.views import View
from django.views.generic import TemplateView
from rest_framework import generics, schemas
from datetime import date, timedelta
from instamojo_wrapper import Instamojo
from my_apis import settings

from braces.views import AjaxResponseMixin, JSONResponseMixin
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.contrib import messages
# from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.authtoken.models import Token

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, get_backends, logout
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from rest_framework.status import HTTP_401_UNAUTHORIZED
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from apis.models import Category, Hotel, Menu, Profile, Cart, CartDetails, PasswordReset, Order, OrderDetails, HotelBranch, HotelAdmin
from .serializers import (CategorySerializer, HotelResultsSerializer, MenuSerializer, AuthCustomTokenSerializer,
                          CartDetailsSerializer, ForgetPasswordSerializer, OrderSerializer, OrderDetailsSerializer, ProfileSerializer,
                          HotelOrderSerializer)
from  my_apis.utils import create_username, SendEmail
from my_apis.mixins import ControlMixin
from apis.forms import AddLocationForm, AddMenuForm, ContactUsForm, LoginForm, SignupForm, ForgotPasswordForm, ResetPasswordForm, OrderForm
from my_apis.settings import GOOGLE_MAPS_GEOLOCATION_KEY
import json
import requests
import httplib
from my_apis import settings
# from googlemaps import GoogleMaps

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

    def get(self,request, *args, **kwargs):
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
            list = HotelBranch.objects.filter(location__distance_lt=(point, Distance(km=radius)))

            for each in list:
                if Menu.objects.filter(hotel_branch=each):
                    new_list.append(each)

            serializer = HotelResultsSerializer(new_list, many=True)
            # return Response(data=lsit_1, status=status.HTTP_200_OK, content_type="application/json")
            return Response(serializer.data)

class HotelMenuView(APIView):
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
            return HotelBranch.objects.get(pk=pk)
        except Hotel.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        hotel_branch = self.get_object(pk)
        menu = Menu.objects.filter(hotel_branch=hotel_branch)
        serializer = MenuSerializer(menu, many=True)
        if not menu:
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "No Menu items.",
                },
                'details': []
            }
            return Response(content, status.HTTP_200_OK)
        else:
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Menu items",
                },
                'details': serializer.data
            }
            return Response(content, status.HTTP_200_OK)


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


        # conn = http.client.HTTPConnection("api.msg91.com")
        #
        # conn.request("GET",
        #              "/api/sendhttp.php?sender=MSGIND&route=4&mobiles=7011925220&authkey=213198AK91IRPFWN5ae7efcf&encrypt=&country=0&message=Hello!%20This%20is%20a%20test%20message&flash=&unicode=&schtime=&afterminutes=&response=&campaign=")
        #
        # res = conn.getresponse()
        # data = res.read()
        #
        # print(data.decode("utf-8"))

        # url = "/api/sendhttp.php?sender=MSGIND&route=4&mobiles=7011925220&authkey=213198AK91IRPFWN5ae7efcf&encrypt=&country=0&message=Hello!%20This%20is%20a%20test%20message&flash=&unicode=&schtime=&afterminutes=&response=&campaign="
        # r = requests.get(url)
        # print r

        conn = httplib.HTTPConnection("control.msg91.com")
        payload = ""
        # conn.request("GET",
        #              "/api/sendhttp.php?sender=MSGIND&route=4&mobiles=7011925220&authkey=213198AK91IRPFWN5ae7efcf&encrypt=&country=0&message=Hello!%20This%20is%20a%20test%20message&flash=&unicode=&schtime=&afterminutes=&response=&campaign=")

        conn.request("POST",
                     "/api/sendotp.php?template=&otp_length=6&authkey213198AK91IRPFWN5ae7efc=&message=Your Otp is:&sender=OTPSMS&mobile=7011925220&otp=701198&otp_expiry=&email=",
                     payload)

        res = conn.getresponse()
        data = res.read()
        print "the data is:", data


        user.is_active = True
        user.save()
        profile, created = Profile.objects.get_or_create(user=user)
        profile.contact = phone
        profile.complete=True
        profile.save()

        username = user.username
        user_login = authenticate(username=username, password=password)
        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                },
                'token': token.key,
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
        # content = {
        #     'status': {
        #         'isSuccess': True,
        #         'code': "SUCCESS",
        #         'message': "Success"
        #     }
        # }
        #
        # return Response(content, status.HTTP_200_OK)

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
                    'error': "Either email or password is incorrect.",
                }
                return Response(content, status.HTTP_400_BAD_REQUEST)

            username = user_request.username
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    profile = Profile.objects.get(user=user)
                    token, created = Token.objects.get_or_create(user=user)
                    content = {
                        'status': {
                            'isSuccess': True,
                            'code': "SUCCESS",
                            'message': "Success"
                        },
                        'token': token.key,
                        'employee': serializer.data,
                        'contact': profile.contact,
                        'name': user.first_name,
                        'id': user.id
                    }

                    return Response(content, status.HTTP_200_OK)
                else:
                    content = {
                        'status': {
                            'isSuccess': False,
                            'code': "FAILURE",
                            'message': "Permission Denied",
                        },
                        'error': "User not active."
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
                qty = qty,
                product_name = obj.name,
            )

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


class CartDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        if user:
            cart = Cart.objects.filter(customer=user).first()
            details = CartDetails.objects.filter(cart=cart)
            serializer = CartDetailsSerializer(details, many=True)
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                },
                'details': serializer.data
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

class ForgetPasswordView(APIView):
    api_docs = {
        'post': {
            'fields': [
                {
                    'name': 'email',
                    'required': True,
                    'description': 'Email of user',
                    'type': 'string'
                }
            ]
        }
    }

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user_request = User.objects.get(email__iexact=email)
            except:
                content = {
                    'status': {
                        'isSuccess': False,
                        'code': "FAILURE",
                        'message': "Invalid Credentials",
                    },
                    'error': "Email Not registered with us."
                }
                return Response(content, status.HTTP_400_BAD_REQUEST)

            PasswordReset.objects.filter(user=user_request).delete()
            password_reset = PasswordReset(user=user_request)
            password_reset.save()

            current_site = get_current_site(request)

            email_sender = SendEmail(request)
            email_sender.send([user_request.email], "email_messages/forget-password.html",
                              {'user': user_request, 'domain': current_site.domain,
                               'token': password_reset.token,
                               },
                              "Reset your password", [])
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success. Email sent successfully"
                },
                'token': password_reset.token
            }

            return Response(content, status.HTTP_200_OK)

class ResetPasswordView(APIView):
    pass


class UserOrdersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        if user:
            profile = Profile.objects.filter(user=user).first()
            orders = Order.objects.filter(customer=profile)

            if not orders:
                content = {
                    'status': {
                        'isSuccess': True,
                        'code': "SUCCESS",
                        'message': "No Orders Yet",
                    },
                    'details': []
                }
                return Response(content, status.HTTP_200_OK)
            else:
                serializer = OrderSerializer(orders, many=True)
                content = {
                    'status': {
                        'isSuccess': True,
                        'code': "SUCCESS",
                        'message': "You have Orders",
                    },
                    'details': serializer.data
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

class UserOrderDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, order_id, *args, **kwargs):
        user = self.request.user
        if user:
            order = Order.objects.filter(order_id=order_id).first()
            order_details = OrderDetails.objects.filter(order=order)
            serializer = OrderDetailsSerializer(order_details, many=True)
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Order Details",
                },
                'details': serializer.data
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

class UserDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    api_docs = {
        'put': {
            'fields': [
                {
                    'name': 'first_name',
                    'required': False,
                    'description': 'First name',
                    'type': 'string'
                },
                {
                    'name': 'last_name',
                    'required': False,
                    'description': 'Last Name',
                    'type': 'string'
                },
                {
                    'name': 'email',
                    'required': False,
                    'description': 'Email',
                    'type': 'string'
                },
                {
                    'name': 'contact',
                    'required': False,
                    'description': 'Contact Info',
                    'type': 'number'
                },

            ]
        }
    }

    def get(self, request):
        user = self.request.user
        if user:
            profile = Profile.objects.filter(user=user).first()
            serializer = ProfileSerializer(profile)
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "profile details",
                },
                'details': serializer.data
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

    def put(self, request):
        user = self.request.user
        if user:
            profile = Profile.objects.filter(user=user).first()
            serializer = ProfileSerializer(profile, data=request.data)
            print "the serializer is:", serializer
            if serializer.is_valid():
                serializer.user=self.request.user.id
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:

            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "User not logged in",
                }
            }

            return Response(content, status.HTTP_400_BAD_REQUEST)

class UserUpdateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    api_docs = {
        'post': {
            'fields': [
                {
                    'name': 'first_name',
                    'required': False,
                    'description': 'First name',
                    'type': 'string'
                },
                {
                    'name': 'last_name',
                    'required': False,
                    'description': 'Last Name',
                    'type': 'string'
                },
                {
                    'name': 'email',
                    'required': False,
                    'description': 'Email',
                    'type': 'string'
                },
                {
                    'name': 'contact',
                    'required': False,
                    'description': 'Contact Info',
                    'type': 'number'
                },

            ]
        }
    }

    def post(self, request, pk):
        user = self.request.user
        if user:
            user = User.objects.get(id=pk)
            profile = Profile.objects.filter(user=user).first()
            serializer = ProfileSerializer(user, data=request.data)
            print "the serializer is:", serializer
            if serializer.is_valid():
                serializer.user = self.request.user.id
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "User not logged in",
                }
            }

            return Response(content, status.HTTP_400_BAD_REQUEST)


class HotelOrdersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Hotel.objects.get(pk=pk)
        except Hotel.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        hotel = self.get_object(pk)
        if hotel.user == request.user:
            print "hotel name", hotel.name
            order = Order.objects.filter(hotel=hotel)
            print "the orders are:", order
            serializer = HotelOrderSerializer(order, many=True)
            print "The serializer data is:", serializer.data
            if order:
                content = {
                    'status': {
                        'isSuccess': True,
                        'code': "SUCCESS",
                        'message': "Order Items.",
                    },
                    'details': serializer.data
                }
                return Response(content, status.HTTP_200_OK)

            else:
                content = {
                    'status': {
                        'isSuccess': True,
                        'code': "SUCCESS",
                        'message': "Sorry No Order Items.",
                    },
                    'details': []
                }
                return Response(content, status.HTTP_200_OK)
        else:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Sorry, You cannot view other hotel orders",
                },
            }
            return Response(content, status.HTTP_400_BAD_REQUEST)


##Beginning of views of dashboard.APIS to be written above it only.##

class DashBoardView(TemplateView, LoginRequiredMixin, ControlMixin):
    template_name = 'dashboard/index.html'

    def get_context_data(self,**kwargs):
        context = super(DashBoardView,self).get_context_data(**kwargs)
        user = self.request.user
        admin = HotelAdmin.objects.filter(user=user).first()
        orders = Order.objects.filter(hotel=admin.hotel).filter(date=date.today())
        amount = 0
        for item in orders:
            if item.accepted:
                amount = amount + int(item.total_amount)

        # context['branch'] = branch
        context['orders'] = orders
        context['count'] = orders.count()
        context['amount'] = amount
        context['admin'] = admin
        context['date'] = date.today()
        context['key_id'] = settings.RAZORPAY_KEY_ID
        return context
        # else:
        #     status_user = True
        #     context = {'status_user': status_user}
        #     return render(self.request, 'dashboard/page-login.html', context)



class VendorLoginView(View):
    template_name = "dashboard/page-login.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email')
        password = self.request.POST.get('password')

        user = User.objects.filter(email__iexact=email).first()

        if not user:
            status_user = True
            context = {'status_user': status_user}
            return render(request, self.template_name, context)

        username = user.username

        user = authenticate(username=username, password=password)

        if user is not None:
            logout(request)
            login(request, user)
            admin = HotelAdmin.objects.filter(user=user).first()
            if admin:
                # url = "/hotel/" + str(admin.hotel.id) + "/dashboard/"
                url = "/hotel/dashboard/"
                return HttpResponseRedirect(url)

            else:
                status = True
                context = {'status': status}
                return render(request, self.template_name, context)


class VendorLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("/vendor/login/")

class CustomerOrderDetails(TemplateView, LoginRequiredMixin, ControlMixin):
    template_name = 'dashboard/table-basic.html'

    def get_context_data(self,**kwargs):
        context = super(CustomerOrderDetails,self).get_context_data(**kwargs)
        order = Order.objects.filter(id=kwargs['pk']).first()
        order_details = OrderDetails.objects.filter(order=kwargs['pk'])
        context['details'] = order_details
        context['order'] = order
        context['admin'] =  HotelAdmin.objects.filter(user=self.request.user).first()
        return context


class VendorMenuView(TemplateView, LoginRequiredMixin, ControlMixin):
    template_name = 'dashboard/restaurant-menu-two.html'

    def get_context_data(self,**kwargs):
        context = super(VendorMenuView,self).get_context_data(**kwargs)
        user = self.request.user
        admin = HotelAdmin.objects.filter(user=user).first()
        # hotel = Hotel.objects.filter(id=kwargs['pk']).first()
        menu = Menu.objects.filter(hotel=admin.hotel)
        context['menu'] = menu
        context['admin'] = HotelAdmin.objects.filter(user=self.request.user).first()
        return context


class VendorLocationListView(TemplateView, LoginRequiredMixin):
    template_name = 'dashboard/restaurant-menu-one.html'

    def get_context_data(self,**kwargs):
        context = super(VendorLocationListView,self).get_context_data(**kwargs)
        user = self.request.user
        admin = HotelAdmin.objects.filter(user=user).first()
        loc_list = HotelBranch.objects.filter(hotel=admin.hotel)
        context['loc_list'] = loc_list
        context['admin'] = HotelAdmin.objects.filter(user=self.request.user).first()
        return context

class VendorLocationAddView(TemplateView, LoginRequiredMixin):
    template_name = 'dashboard/form-basic.html'

    def get_context_data(self, **kwargs):
        context = super(VendorLocationAddView, self).get_context_data(**kwargs)
        form = AddLocationForm(self.request.POST or None)
        context['form'] = form
        context['admin'] = HotelAdmin.objects.filter(user=self.request.user).first()
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        admin = HotelAdmin.objects.filter(user=user).first()
        form = AddLocationForm(self.request.POST)
        if form.is_valid():
            hotel_branch = form.save(commit=False)
            hotel_branch.hotel = admin.hotel

            ##Converting address to lat, long using google maps request
            address = form.cleaned_data['address'] + ',' + form.cleaned_data['city'] + ',' + form.cleaned_data['state'] + 'IN'
            api_key = GOOGLE_MAPS_GEOLOCATION_KEY
            api_response = requests.get(
                'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'OK':
                latitude = api_response_dict['results'][0]['geometry']['location']['lat']
                longitude = api_response_dict['results'][0]['geometry']['location']['lng']
            hotel_branch.lat = latitude
            hotel_branch.long = longitude
            hotel_branch.save()

            url = '/hotel/dashboard/'
            return HttpResponseRedirect(url)
        else:
            status = True
            context = {'status': status}
            return render(request, self.template_name, context)


class VendorLocationUpdateView(TemplateView, LoginRequiredMixin):
    template_name = 'dashboard/vendor-location-update.html'

    def get_context_data(self, **kwargs):
        context = super(VendorLocationUpdateView, self).get_context_data(**kwargs)
        hotel_branch = HotelBranch.objects.filter(id=kwargs['pk']).first()
        print "the hotel branch is:", hotel_branch
        form = AddLocationForm(self.request.POST or None)
        context['form'] = form
        context['branch'] = hotel_branch
        context['admin'] = HotelAdmin.objects.filter(user=self.request.user).first()
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        admin = HotelAdmin.objects.filter(user=user).first()
        hotel_branch = HotelBranch.objects.filter(id=kwargs['pk']).first()
        form = AddLocationForm(self.request.POST, instance=hotel_branch)
        print "The form is:", form
        if form.is_valid():
            form.save()
            url = '/vendor/location/'
            return HttpResponseRedirect(url)
        else:
            print "Inside Form Invalid"
            status = True
            context = {'status': status}
            return render(request, self.template_name, context)


class VendorMenuUploadView(TemplateView, LoginRequiredMixin):
    template_name = 'dashboard/restaurant-upload-menu.html'

    def get_context_data(self, **kwargs):
        context = super(VendorMenuUploadView, self).get_context_data(**kwargs)
        admin = HotelAdmin.objects.filter(user=self.request.user).first()
        form = AddMenuForm(self.request.POST or None, self.request.FILES or None)
        context['form'] = form
        context['admin'] = HotelAdmin.objects.filter(user=self.request.user).first()
        context['category'] = Category.objects.all()
        context['branch'] = HotelBranch.objects.filter(hotel = admin.hotel)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        user = request.user
        admin = HotelAdmin.objects.filter(user=user).first()
        form = context['form']
        if form.is_valid():
            menu = form.save(commit=False)
            menu.hotel = admin.hotel
            menu.image = request.FILES.get("image")
            menu.type=form.cleaned_data['type']
            menu.save()
            url = '/vendor/menu'
            return HttpResponseRedirect(url)
        else:
            context['form'] = form
            return render(request, self.template_name, context)



class VendorOrderListView(TemplateView, LoginRequiredMixin):
    template_name = 'dashboard/restaurant-order-list.html'

    def get_context_data(self, **kwargs):
        context = super(VendorOrderListView, self).get_context_data(**kwargs)
        admin = HotelAdmin.objects.filter(user=self.request.user).first()
        amount = 0
        orders = Order.objects.filter(hotel=admin.hotel)
        for each in orders:
            if each.accepted:
                amount = amount + int(each.total_amount)
        context['orders'] = orders
        context['admin'] = HotelAdmin.objects.filter(user=self.request.user).first()
        context['amount'] = amount
        context['count'] = orders.count()
        return context

class VerifyPaymentView(AjaxResponseMixin, JSONResponseMixin, View):

    def get_ajax(self, request, *args, **kwargs):
        print "inside Get"
        response = {'status': False, 'errors': [], 'data': 0}
        payment_key = self.request.GET.get('payment_key')
        payment_price = self.request.GET.get('payment_price')
        order_id = self.request.GET.get('order_id')
        print order_id
        url = 'https://api.razorpay.com/v1/payments/' + payment_key + '/capture'
        r = requests.post(url, data={'amount': payment_price},
                          auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_KEY))
        print "the something is:", r.status_code, self.request.GET.get('payment_key')

        response['redirect_url'] = '/order/confirmation/' + order_id + '/'
        response['status'] = True
        return self.render_json_response(response)

    # def post_ajax(self, request, *args, **kwargs):
    #     print "inside Post"
    #     response = {'status': False, 'errors': [], 'data': 0}
    #     payment_key = self.request.GET.get('payment_key')
    #     payment_price = self.request.GET.get('payment_price')
    #     order_id = self.request.GET.get('order_id')
    #     print order_id
    #     url = 'https://api.razorpay.com/v1/payments/' + payment_key + '/capture'
    #     r = requests.post(url, data={'amount': payment_price},
    #                       auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_KEY))
    #     print "the something is:", r.status_code, self.request.GET.get('payment_key')
    #
    #     response['redirect_url'] = '/order/confirmation/' + order_id + '/'
    #     response['status'] = True
    #     return self.render_json_response(response)

class HomeView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['form'] = ContactUsForm(self.request.POST)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form']
        if form.is_valid():
            contact = form.save(commit=False)
            contact.save()
            context['status'] = True
            return render(request, self.template_name, context)

        else:
            context['form'] = form
            return render(request, self.template_name, context)

class RestaurantListView(TemplateView):
    template_name = 'website/list_page.html'

    def get_context_data(self, **kwargs):
        context = super(RestaurantListView, self).get_context_data(**kwargs)
        keyword = self.request.GET.get('keyword')

        if keyword:
            hotelbranch = HotelBranch.objects.filter(
                id__in=Menu.objects.filter(
                    Q(hotel_branch__branch_name__icontains=keyword) |
                    Q(hotel_branch__hotel__name__icontains=keyword) |
                    Q(hotel_branch__address__icontains=keyword) |
                    Q(hotel_branch__city__icontains=keyword) |
                    Q(hotel_branch__state__icontains=keyword) |
                    Q(category__category__icontains=keyword) |
                    Q(name__icontains=keyword)
                ).values_list("hotel_branch__id", flat=True)
            )
            hotel_count = hotelbranch.count()
        else:
            hotelbranch = HotelBranch.objects.all()
            hotel_count = hotelbranch.count()
            # for each in category:
            #     dict_num = {each.category: 0}
            #     cat_count.update(dict_num)
            #
            # for each in menu:
            #     for key, value in cat_count.iteritems():
            #         if each.category.category == key:
            #             cat_count[key] = value + 1
            #

        context['hotelbranch'] = hotelbranch
        context['hotel_count'] = hotel_count

        # context['category'] = category
        # context['category_count'] = category_count
        # context['cat_count'] = cat_count

        return context

class RestaurantMenuView(TemplateView):
    template_name = 'website/detail_page.html'

    def get_context_data(self, **kwargs):
        context = super(RestaurantMenuView, self).get_context_data(**kwargs)
        menu = Menu.objects.filter(hotel_branch=kwargs['pk'])
        categories = Category.objects.filter(
            id__in=Menu.objects.filter(hotel_branch=kwargs['pk']).values_list("category", flat=True).distinct()
        )
        hotel = HotelBranch.objects.get(id=kwargs['pk'])
        category = Category.objects.all()
        cat_count = dict()

        context['menu'] = menu
        context['hotel'] = hotel
        context['cat_count'] = cat_count
        context['category'] = category
        context['categories'] = categories
        context['pk']=kwargs['pk']

        return context

class LoginView(AjaxResponseMixin, JSONResponseMixin, View):

    def dispatch(self, request, *args, **kwargs):
        """
        Check to see if the user in the request has the required
        permission.
        """
        if request.method == "GET":
            return redirect("/")

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post_ajax(self, request, *args, **kwargs):
        """
            Login the user after successful authentication
        """
        response = {'status': False, 'errors': []}

        form = LoginForm(request.POST, request=request)
        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.get(email__iexact=email)
            username = user.username

            user = authenticate(username=username, password=password)

            if user is not None:
                logout(request)
                login(request, user)
                response['status'] = True
            else:
                # TODO Need to send email verification link again.
                response['errors'].append({"key": "__all__", "error": "* You did not verify your account yet. Please check your email and verify your account."})

        else:
            for key, value in form.errors.iteritems():
                tmp = {'key': key, 'error': value.as_text()}
                response['errors'].append(tmp)

        return self.render_json_response(response)

class LogoutView(View):

    def get(self, request, *args, **kwargs):
        print "here"
        logout(request)
        return redirect("/")

class SignupView(AjaxResponseMixin, JSONResponseMixin, View):

    def dispatch(self, request, *args, **kwargs):
        """
        Check to see if the user in the request has the required
        permission.
        """
        if request.method == "GET":
            return redirect("/")

        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def post_ajax(self, request, *args, **kwargs):
        """
            Signup the user first and then sigin the user.
        """
        response = {'status': False, 'errors': []}

        form = SignupForm(request.POST, request=request)

        if form.is_valid():
            profile = form.save()
            email = form.cleaned_data['email']
            user = User.objects.get(email__iexact=email)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)

            try:
                email_sender = SendEmail(request)
                email_sender.send([user.email], "email_messages/account_active_email.html",
                                                            {'user': user, 'domain': current_site.domain,
                                                             'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                                             'token': default_token_generator.make_token(user),
                                                             },
                                                            "Activate your Queued account", [])
            except:
                pass
            response['status'] = True
            return self.render_json_response(response)
        else:

            # Django simple captcha view

            # data = render_to_string("account/signup_modal.html", {'signup_form': form}, request=request)
            # response['data'] = data

            for key, value in form.errors.iteritems():
                tmp = {'key': key, 'error': value.as_text()}
                response['errors'].append(tmp)

        return self.render_json_response(response)



class ContactView(AjaxResponseMixin, JSONResponseMixin, View):

    def dispatch(self, request, *args, **kwargs):
        """
        Check to see if the user in the request has the required
        permission.
        """
        if request.method == "GET":
            return redirect("/")

        return super(ContactView, self).dispatch(request, *args, **kwargs)

    def post_ajax(self, request, *args, **kwargs):
        print "here"
        """
            Signup the user first and then sigin the user.
        """
        response = {'status': False, 'errors': []}

        form = ContactUsForm(request.POST, request=request)

        if form.is_valid():
            print "inside form valid"
            email = form.cleaned_data['email']
            name_obj = form.cleaned_data['name']
            contact_obj = form.save()
            # email = form.cleaned_data['email']
            # user = User.objects.get(email__iexact=email)
            # user.is_active = False
            # user.save()

            current_site = get_current_site(request)

            try:
                email_sender = SendEmail(request)
                email_sender.send([email], "email_messages/thank_you.html",
                                                            {'name':name_obj
                                                             },
                                                            "Thank You", [])
            except:
                pass
            response['status'] = True
            return self.render_json_response(response)
        else:
            print "inside form invalid"
            print form

            # Django simple captcha view

            # data = render_to_string("account/signup_modal.html", {'signup_form': form}, request=request)
            # response['data'] = data

            for key, value in form.errors.iteritems():
                tmp = {'key': key, 'error': value.as_text()}
                response['errors'].append(tmp)

        return self.render_json_response(response)


class EmailAccountActivate(View):

   def get(self, request, **kwargs):
       try:
           uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
           user = User.objects.get(pk=uid)
       except(TypeError, ValueError, OverflowError, User.DoesNotExist):
           user = None

       if user is not None and default_token_generator.check_token(user, kwargs['token']):
           user.is_active = True
           user.save()
           login(request, user)
           return redirect("/")
       else:
           return HttpResponse('Activation link is invalid!')

class ForgotPasswrod(AjaxResponseMixin, JSONResponseMixin, View):

    def dispatch(self, request, *args, **kwargs):
        """
        Check to see if the user in the request has the required
        permission.
        """
        if request.method == "GET":
            return redirect("/")

        return super(ForgotPasswrod, self).dispatch(request, *args, **kwargs)

    def post_ajax(self, request, *args, **kwargs):
        """
        User enter the email for the forgot password. A link will be sent to the verfied email of the user for reset password
        """
        response = {'status': False, 'errors': []}

        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email__iexact=email)

            PasswordReset.objects.filter(user=user).delete()
            password_reset = PasswordReset(user=user)
            password_reset.save()

            current_site = get_current_site(request)

            email_sender = SendEmail(request)
            email_sender.send([user.email], "email_messages/forget-password.html",
                              {'user': user, 'domain': current_site.domain,
                               'token': password_reset.token,
                               },
                              "Reset your password", [])

            response['status'] = True
        else:
            for key, value in form.errors.iteritems():
                tmp = {'key': key, 'error': value.as_text()}
                response['errors'].append(tmp)

        return self.render_json_response(response)


class ResetPasswordView(View):
    template_name = "website/reset_password.html"

    def get(self, request, **kwargs):

        try:
            password_reset = PasswordReset.objects.get(token=kwargs['token'])
        except:
            messages.error(self.request, 'That password reset token is no longer valid, please try again.')
            return redirect("/")

        if password_reset.completed:
            messages.error(self.request, 'You have used this token.')
            return redirect("/")

        form = ResetPasswordForm(None)
        context = {'form': form, 'password_reset': password_reset}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        try:
            password_reset = PasswordReset.objects.get(token=kwargs['token'])
        except PasswordReset.DoesNotExist:
            messages.error(self.request, 'That password reset token is no longer valid, please try again.')
            return redirect("/")

        if password_reset.completed:
            messages.error(self.request, 'You have used this token.')
            return redirect("/")

        form = ResetPasswordForm(self.request.POST)

        if form.is_valid():
            password_reset.user.set_password(form.cleaned_data['password'])
            password_reset.user.save()
            password_reset.completed = True
            password_reset.save()
            messages.success(request, 'Password successfully reset. Please login with your new credentials.')
            return redirect("/")
        else:
            context = {'form': form, 'password_reset': password_reset}
            return render(request, self.template_name, context)


class UserCartView(TemplateView):
    template_name = "website/user_cart.html"

    def get_context_data(self, **kwargs):
        context = super(UserCartView, self).get_context_data(**kwargs)
        cart = Cart.objects.get_or_create(customer=self.request.user)
        cart_details = CartDetails.objects.filter(cart=cart)
        context['cart'] = cart
        context['cart_details'] = cart_details
        return context


class AddCartView(AjaxResponseMixin, JSONResponseMixin, View):
    def get_ajax(self, request, *args, **kwargs):
        response = {'status': False, 'data': '', 'change': False}
        item = request.GET.get('item')
        menu = Menu.objects.get(id=item)
        cart = Cart.objects.get(customer=request.user)
        cd = CartDetails.objects.filter(cart=cart)
        list_re = list()
        for each in cd:
            list_re.append(each.product.hotel_branch.branch_name)

        if not list_re :
            cart_details, created = CartDetails.objects.get_or_create(cart=cart, product=menu)

            if created:
                cart_details.product_name = menu.name
                cart_details.price = menu.price
                cart_details.qty = 1
                cart_details.save()
                response['status'] = True
            else:
                cart_details.price = cart_details.price + menu.price
                cart_details.qty = cart_details.qty + 1
                cart_details.save()
                response['status'] = True

        elif menu.hotel_branch.branch_name in list_re:
            cart_details, created = CartDetails.objects.get_or_create(cart=cart, product=menu)

            if created:
                cart_details.product_name = menu.name
                cart_details.price = menu.price
                cart_details.qty = 1
                cart_details.save()
                response['status'] = True
            else:
                cart_details.price = cart_details.price + menu.price
                cart_details.qty = cart_details.qty + 1
                cart_details.save()
                response['status'] = True


        else:
            response['status'] = False
            response['change'] = True

        return self.render_json_response(response)


class DecrementCartView(AjaxResponseMixin, JSONResponseMixin, View):
    def get_ajax(self, request, *args, **kwargs):
        response = {'status': False, 'data': ''}
        item = request.GET.get('item')
        print "the item is", item
        menu = Menu.objects.get(id=item)
        cart = Cart.objects.get(customer=request.user)
        cart_details, created = CartDetails.objects.get_or_create(cart=cart, product=menu)
        cart_details.qty = cart_details.qty - 1

        if cart_details.qty == 0:
            cart_details.delete()
        else:
            cart_details.price = cart_details.price - menu.price
            cart_details.save()

        response['status'] = True
        return self.render_json_response(response)


class ClearCartView(AjaxResponseMixin, JSONResponseMixin, View):
    def get_ajax(self, request, *args, **kwargs):
        response = {'status': False, 'data': ''}
        cart = Cart.objects.get(customer=request.user)
        CartDetails.objects.filter(cart=cart).delete()
        response['status'] = True
        return self.render_json_response(response)


class OrderNowView(TemplateView):
    template_name = 'website/cart.html'

    def get_context_data(self, **kwargs):
        context = super(OrderNowView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user:
            return HttpResponseRedirect('/')
        else:
            profile = Profile.objects.get(user=user)
            cart = Cart.objects.get(customer=user)
            cart_details = CartDetails.objects.filter(cart=cart).first()
            context['profile'] = profile
            context['cd'] = cart_details
            # context['form'] = OrderForm(self.request.POST or None)
            return context

class CreateOrderView(AjaxResponseMixin, JSONResponseMixin, View):

    def post_ajax(self, request, *args, **kwargs):
        response = {'status': False, 'errors': [], 'data':0}
        form = OrderForm(request.POST)
        cart = Cart.objects.get(customer=request.user)
        cart_details = CartDetails.objects.filter(cart=cart).first()
        amount = 0
        liquor_tax = 0
        food_tax = 0
        amount_bsc = 0  ##Amount before Service Charge
        service_charge = 0

        ## 9811714766 - Rajat Chopra

        total_amount = 0
        cd = CartDetails.objects.filter(cart=cart)
        for item in cd:
            amount = amount + (item.qty * item.product.price)
            if item.product.menu_type == 0:
                liquor_tax_percent = int(item.product.price * 0.18)
                tax_amount = int(item.qty * liquor_tax_percent)
                liquor_tax = liquor_tax + tax_amount
            else:
                food_tax_percent = int(item.product.price * 0.05)
                tax_amount = int(item.qty * food_tax_percent)
                food_tax = food_tax + tax_amount

        amount_bsc = amount_bsc + amount + liquor_tax + food_tax

        if cart_details.product.hotel.service_charge:
            service_charge_percent = (int(cart_details.product.hotel.service_charge_percent) / float(100))
            service_charge = int(amount_bsc * service_charge_percent)

        total_amount = amount_bsc + service_charge

        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.profile
            order.hotel = cart_details.product.hotel
            order.hotel_branch = cart_details.product.hotel_branch
            order.total_amount = amount
            order.food_tax = food_tax
            order.liquor_tax = liquor_tax
            order.service_charge = service_charge
            order.total_incl_amount = total_amount
            order.date = form.cleaned_data['date']
            order.time = form.cleaned_data['time']
            order.special_notes = form.cleaned_data['special_notes']
            order.number_of_persons = form.cleaned_data['number_of_persons']
            order.order_status = 1
            order.payment_status = 3
            order.payment_type = 0
            order.save()

        for each in cd:
            OrderDetails.objects.create(
                order=order,
                name=each.product_name,
                qty=each.qty,
                amount=each.price
            )
        CartDetails.objects.filter(cart=cart).delete()

        buyer_name = order.customer.user.get_full_name()

        ##InstaMojo Testing

        api = Instamojo(api_key="17dc18b558c84e50dcf97dd2ade37624",
                        auth_token="1a733717bcd1fa397dd0d04d3bace0fa")


        # Create a new Payment Request
        response = api.payment_request_create(
            amount=order.total_incl_amount,
            purpose='Payment for Order Number' + str(order.order_id),
            send_email=True,
            email=order.customer.user.email,
            buyer_name=buyer_name,
            phone=order.customer.contact,
            redirect_url="http://127.0.0.1:8000/order/confirmation/instamojo/",
        )

        print response

        order.instamojo_payment_request_id = response['payment_request']['id']
        order.instamojo_payment_long_url = response['payment_request']['longurl']
        order.save()

        response['status'] = True
        response['data'] = order.order_id
        response['instamojo'] = response['payment_request']['longurl']



        # tmp = {'total_amount': int(order.total_amount * 100)}
        # response['data'] = tmp
        # return HttpResponseRedirect(response['payment_request']['longurl'])
        return self.render_json_response(response)


class CreateOrderPayHotelView(AjaxResponseMixin, JSONResponseMixin, View):
    def post_ajax(self, request, *args, **kwargs):
        response = {'status': False, 'errors': [], 'data': 0}
        form = OrderForm(request.POST)
        cart = Cart.objects.get(customer=request.user)
        cart_details = CartDetails.objects.filter(cart=cart).first()
        amount = 0
        liquor_tax = 0
        food_tax = 0
        amount_bsc = 0 ##Amount before Service Charge
        service_charge = 0
        total_amount = 0
        cd = CartDetails.objects.filter(cart=cart)
        for item in cd:
            amount = amount + (item.qty * item.product.price)
            if item.product.menu_type == 0:
                liquor_tax_percent = int(item.product.price * 0.18)
                tax_amount = int(item.qty * liquor_tax_percent)
                liquor_tax = liquor_tax + tax_amount
            else:
                food_tax_percent = int(item.product.price * 0.05)
                tax_amount = int(item.qty * food_tax_percent)
                food_tax = food_tax + tax_amount


        amount_bsc = amount_bsc + amount + liquor_tax + food_tax

        if cart_details.product.hotel.service_charge:
            service_charge_percent = (int(cart_details.product.hotel.service_charge_percent) / float(100))
            service_charge = int(amount_bsc * service_charge_percent)

        total_amount = amount_bsc + service_charge

        if form.is_valid():
            order = form.save(commit=False)
            order.customer=request.user.profile
            order.hotel = cart_details.product.hotel
            order.hotel_branch = cart_details.product.hotel_branch
            order.total_amount=amount
            order.food_tax=food_tax
            order.liquor_tax=liquor_tax
            order.service_charge=service_charge
            order.total_incl_amount=total_amount
            order.date = form.cleaned_data['date']
            order.time = form.cleaned_data['time']
            order.special_notes = form.cleaned_data['special_notes']
            order.number_of_persons = form.cleaned_data['number_of_persons']
            order.order_status = 1
            order.payment_status = 3
            order.payment_type = 1
            order.save()

        else:
            print "inside Form invalid"
            print form.errors

        for each in cd:
            OrderDetails.objects.create(
                order=order,
                name=each.product.name,
                qty=each.qty,
                price=each.product.price,
                amount=each.price,
            )
        CartDetails.objects.filter(cart=cart).delete()
        response['status'] = True
        response['data'] = order.order_id
        response['redirect_url'] = '/order/confirmation/'+ order.order_id +'/'
        # tmp = {'total_amount': int(order.total_amount * 100)}
        # response['data'] = tmp
        # return render(request, 'website/confirmation.html', response)
        return self.render_json_response(response)

class ProfileUpdateView(TemplateView):
    template_name = 'website/profile-update.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        user = self.request.user
        profile = Profile.objects.filter(user=user).first()
        context['profile'] = profile
        return context

    def post(self, request, *args, **kwargs):
        first_name = self.request.POST.get('firstname')
        last_name = self.request.POST.get('lastname')
        phone = self.request.POST.get('tel')

        user = request.user
        profile = Profile.objects.get(user=user)

        profile.user.first_name = first_name
        profile.user.last_name = last_name
        profile.user.save()
        profile.contact = phone
        profile.save()

        return HttpResponseRedirect('/')

class OrdersListView(TemplateView):
    template_name = "website/user-order-list.html"

    def get_context_data(self, **kwargs):
        context = super(OrdersListView, self).get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        orders = Order.objects.filter(customer=profile).order_by('-date')
        context['orders'] = orders
        return context

class OrderDetailView(TemplateView):
    template_name = "website/user-order-detail.html"

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        order = Order.objects.filter(id=kwargs['pk']).first()
        order_details = OrderDetails.objects.filter(order=order)
        context['order'] = order
        context['order_details'] = order_details
        return context

class OrderConfirmationView(TemplateView):
    template_name = 'website/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super(OrderConfirmationView, self).get_context_data(**kwargs)
        order = Order.objects.get(order_id=kwargs['order_id'])
        order_details = OrderDetails.objects.filter(order=order)
        context['order']=order
        context['order_details']=order_details
        return context

class InstamojoOrderConfirmationView(TemplateView):
    template_name = 'website/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super(InstamojoOrderConfirmationView, self).get_context_data(**kwargs)
        payment_request_id = self.request.GET.get('payment_request_id')
        payment_id = self.request.GET.get('payment_id')
        api = Instamojo(api_key="17dc18b558c84e50dcf97dd2ade37624",
                        auth_token="1a733717bcd1fa397dd0d04d3bace0fa")

        # Create a new Payment Request
        response = api.payment_request_payment_status(str(payment_request_id), str(payment_id))
        print response['payment_request']['purpose']  # Purpose of Payment Request
        print response['payment_request']['payment']['status']  # Payment status

        if response['payment_request']['payment']['status'] == True:
            try:
                order = Order.objects.get(instamojo_payment_request_id=payment_request_id)
            except:
                context['failure']=True
                context['order'] = order
                return context

            order.instamojo_payment_id=payment_id
            order.payment_status=1
            order.save()
            context['failure'] = False
            context['order'] = order
            order_details = OrderDetails.objects.filter(order=order)
            context['order_details'] = order_details
            return context

        else:
            order = Order.objects.get(instamojo_payment_request_id=payment_request_id)
            context['failure'] = True
            context['order'] = order
            return context

        # print response['payment_request']['shorturl']  # Get the short URL
        # print response['payment_request']['status']  # Get the current status
        # print response['payment_request']['payments']  # List of payments
        #
        # order = Order.objects.get(instamojo_payment_request_id=self.request.GET.get('payment_request_id'))
        # if order:
        #     order.instamojo_payment_id = self.request.GET.get('payment_id')
        #     order.save()
        # order_details = OrderDetails.objects.filter(order=order)
        # context['order']=order
        # context['order_details']=order_details
        # return context
