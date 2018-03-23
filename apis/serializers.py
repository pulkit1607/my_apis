from rest_framework import serializers
from .models import Category, Hotel, Menu, CartDetails, Order, OrderDetails
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

class HotelResultsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotel
        fields = ('id', 'name', 'contact_number', 'address', 'city', 'state', 'lat', 'long')

class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = ('id', 'name', 'decscription', 'price')

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

    hotel = HotelNameSerializer()
    class Meta:
        model = Order
        fields = ('order_id', 'total_amount', 'hotel')

class OrderDetailsSerializer(serializers.ModelSerializer):

    order = OrderSerializer()
    class Meta:
        model = OrderDetails
        fields = ('name', 'amount', 'order')