# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from hashlib import md5
from random import random

from random import randint
# Create your models here.

class Category(models.Model):
    category = models.CharField(max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.category


class Hotel(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.name

class HotelBranch(models.Model):
    branch_name = models.CharField(max_length=250, null=True, blank=True)
    hotel = models.ForeignKey(Hotel)
    contact_number = models.CharField(max_length=250, null=True, blank=True)
    contact_person_name = models.CharField(max_length=250, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    long = models.FloatField(null=True, blank=True)
    location = models.PointField(null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.branch_name

    def save(self, *args, **kwargs):
        lat = self.lat
        long = self.long
        self.location = Point(long,lat)
        super(HotelBranch, self).save(*args, **kwargs)


class HotelAdmin(models.Model):
    user = models.ForeignKey(User)
    hotel_branch = models.ForeignKey(HotelBranch, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username


class Profile(models.Model):
    user = models.OneToOneField(User)
    contact = models.CharField(max_length=250, null=True, blank=True)
    complete = models.BooleanField(default=False)  ### Check for profile complete ###
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username



class Menu(models.Model):
    hotel = models.ForeignKey(Hotel)
    category = models.ForeignKey(Category)
    hotel_branch = models.ForeignKey(HotelBranch, null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    decscription = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    price = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.hotel)

class Order(models.Model):
    customer = models.ForeignKey(Profile)
    order_id = models.CharField(max_length=32, unique=True)
    hotel = models.ForeignKey(Hotel)
    hotel_branch = models.ForeignKey(HotelBranch, null=True, blank=True)
    total_amount = models.CharField(max_length=50, null=True)
    date = models.DateField(null=True, blank=False)
    time = models.CharField(max_length=100, null=True, blank=True)
    number_of_persons = models.IntegerField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = get_unique_order_id(self)
        super(Order, self).save(*args, **kwargs)


    def __unicode__(self):
        return self.order_id


class OrderDetails(models.Model):
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=300, null=True)
    qty = models.IntegerField(default=1, null=True, blank=True)
    amount = models.CharField(max_length=250, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s <%s> ' % (self.name, self.order.order_id)


class Refund(models.Model):
    refund_id = models.CharField(max_length=32, unique=True)
    order = models.ForeignKey(Order)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.refund_id

    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = get_unique_refund_id(self)
        super(Refund, self).save(*args, **kwargs)



class Cart(models.Model):
    customer = models.OneToOneField(User)

    def __unicode__(self):
        return self.customer.username

class CartDetails(models.Model):
    cart = models.ForeignKey(Cart)
    product = models.ForeignKey(Menu)
    product_name = models.CharField(max_length=250, null=True, blank=True)
    price = models.IntegerField(default=0, null=True, blank=True)
    qty = models.IntegerField(default=1, null=True, blank=True)



class PasswordReset(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=32, null=True, blank=True, unique=True)
    completed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s Token' % self.user

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = md5(str(random())).hexdigest()
        super(PasswordReset, self).save(*args, **kwargs)


def get_unique_order_id(instance):
    unique_id = "{0:10d}".format(randint(1, 10000000000)).replace(" ", "0")

    if Order.objects.filter(order_id=unique_id).exists():
        get_unique_order_id(instance)
    return unique_id

def get_unique_refund_id(instance):
    unique_id = "{0:10d}".format(randint(1, 10000000000)).replace(" ", "0")

    if Refund.objects.filter(refund_id=unique_id).exists():
        get_unique_refund_id(instance)
    return unique_id
