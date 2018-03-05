# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    category = models.CharField(max_length=250, null=True, blank=True)


    def __unicode__(self):
        return self.category

class Profile(models.Model):
    user = models.OneToOneField(User)
    contact = models.CharField(max_length=250, null=True, blank=True)
    complete = models.BooleanField(default=False)  ### Check for profile complete ###
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username

class Hotel(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
