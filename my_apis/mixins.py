import json

from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_backends, logout
from apis.models import HotelAdmin


class ControlMixin(object):

    def dispatch(self, request, *args, **kwargs):
        print "the requested user is:", request.user
        list = HotelAdmin.objects.all()
        if request.user in list:
            return super(ControlMixin, self).dispatch(request, *args, **kwargs)
        else:
            logout(request)
            messages.add_message(request, messages.WARNING, "You don't have permissions to access that page.")
            return redirect("/vendor/login/")
