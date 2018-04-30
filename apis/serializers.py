from rest_framework import serializers
from .models import Category, Hotel, Menu, CartDetails, Order, OrderDetails, Profile, HotelBranch, HotelAdmin
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

class HotelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotel
        fields = ('id', 'name')

class HotelResultsSerializer(serializers.ModelSerializer):

    hotel = HotelSerializer()
    class Meta:
        model = HotelBranch
        fields = ('id', 'hotel', 'branch_name', 'contact_number', 'contact_person_name', 'address', 'city', 'state', 'lat', 'long')

class MenuSerializer(serializers.ModelSerializer):

    hotel_branch = HotelResultsSerializer()
    class Meta:
        model = Menu
        fields = ('id', 'name', 'decscription', 'price', 'image', 'hotel', 'hotel_branch', 'category')

class AuthCustomTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CartDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartDetails
        fields = ('product_name', 'price', 'qty')


class HotelNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotel
        fields = ('__all__')


class OrderSerializer(serializers.ModelSerializer):

    hotel_branch = HotelResultsSerializer()
    class Meta:
        model = Order
        fields = ('order_id', 'total_amount', 'hotel_branch', 'date', 'time', 'number_of_persons')

class OrderDetailsSerializer(serializers.ModelSerializer):

    order = OrderSerializer()
    class Meta:
        model = OrderDetails
        fields = ('name', 'amount', 'order')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    class Meta:
        model = Profile
        fields = ('user', 'contact')


class HotelOrderSerializer(serializers.ModelSerializer):

    customer = ProfileSerializer()
    class Meta:
        model = Order
        fields = ('order_id', 'total_amount', 'time', 'customer')