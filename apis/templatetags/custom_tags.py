from __future__ import division
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
    return menu_obj.price

@register.assignment_tag
def get_tax(user_cart_details):
    tax_total = 0
    for each in user_cart_details:
        print each
        if each.product.menu_type == 1:
            product_tax = each.product.price * 0.05
            total_product_tax = each.qty * product_tax
            tax_total = tax_total + total_product_tax
        # else:
        #     print "here 2"
        #     product_tax = int(each.product.price * 0.18)
        #     total_product_tax = int(each.qty * product_tax)
        #     tax_total = tax_total + total_product_tax
        # tax_total = tax_total + (each.qty * int(each.product.price * int(each.product.tax_percent/100)))
    return tax_total

@register.assignment_tag
def get_liquor_status(user_cart_details):
    for each in user_cart_details:
        if each.product.menu_type == 0:
            return True


@register.assignment_tag
def get_liquor_tax(user_cart_details):
    tax_total = 0
    for each in user_cart_details:
        if each.product.menu_type == 0:
            product_tax = int(each.product.price * 0.18)
            total_product_tax = int(each.qty * product_tax)
            tax_total = tax_total + total_product_tax

    return tax_total

@register.assignment_tag
def get_service_charge_status(user_cart_details):
    for each in user_cart_details:
        if each.product.hotel.service_charge == True:
            return True

@register.assignment_tag
def get_service_charge_amount(user_cart_details):
    price = 0
    total = get_total(user_cart_details)
    food_tax = get_tax(user_cart_details)
    liquor_status = get_liquor_status(user_cart_details)
    if liquor_status:
        liquor_tax = get_liquor_tax(user_cart_details)
        price = total + food_tax + liquor_tax
        for each in user_cart_details:
            if each.product.hotel.service_charge == True:
                service_tax = (int(each.product.hotel.service_charge_percent) / float(100))
                price = int(price * service_tax)
                return price
    else:
        price = total + food_tax
        for each in user_cart_details:
            if each.product.hotel.service_charge == True:
                service_tax = (int(each.product.hotel.service_charge_percent) / float(100))
                price = int(price * service_tax)
                return price


@register.assignment_tag
def get_tax_total(total, tax, liquor_tax, user_cart_details):
    status = get_service_charge_status(user_cart_details)
    if status:
        service_charge = get_service_charge_amount(user_cart_details)
        if liquor_tax:
            return total + tax + liquor_tax + service_charge
        else:
            return total + tax +  service_charge
    else:
        if liquor_tax:
            return total + tax + liquor_tax
        else:
            return total + tax

@register.assignment_tag
def get_price(name, id):
    menu = Menu.objects.filter(hotel_branch=id, name=name).first()
    return menu.price
