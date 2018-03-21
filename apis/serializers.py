from rest_framework import serializers
from .models import Category, Hotel, Menu, CartDetails
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

class CartDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartDetails
        fields = ('product_name', 'price', 'qty')