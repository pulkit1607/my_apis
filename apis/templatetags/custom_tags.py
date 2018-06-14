from django.db.models import Q
from django.template import Library
import urlparse
from django.contrib import admin
from django.template import Template
from django.utils.safestring import mark_safe
from django.http import HttpResponseForbidden
# from django.template.loader import render_to_string
from django.template.loader import render_to_string
from apis.models import Menu, Category
from django import template
register = Library()

@register.assignment_tag
def get_menu(menu_id, category_id):
    menu = Menu.objects.filter(category=category_id, hotel_branch=menu_id)
    print menu
    return menu

@register.assignment_tag
def get_total(user_cart_details):
    total = 0
    for item in user_cart_details:
        total = total + item.price
    return total

@register.assignment_tag
def get_individual_price(id):
    menu_obj = Menu.objects.get(id=id)
    print menu_obj
    return menu_obj.price