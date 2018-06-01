from django import forms
from django.contrib.auth.models import User

from apis.models import HotelBranch, Menu, ContactForm

class AddLocationForm(forms.ModelForm):

    class Meta:
        model=HotelBranch
        exclude = ('hotel', 'lat', 'long', 'location', 'objects')

class AddMenuForm(forms.ModelForm):

    class Meta:
        model = Menu
        exclude = ('hotel', )

class ContactUsForm(forms.ModelForm):

    class Meta:
        model = ContactForm
        exclude = {}