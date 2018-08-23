from django.shortcuts import render, redirect, get_object_or_404
from apis.forms import LoginForm, SignupForm, ForgotPasswordForm, ContactUsForm
from apis.models import Cart, CartDetails
from my_apis.settings import RAZORPAY_KEY_ID

def form_context(request):
    # pass the login, signup and forgot password form in all pages as a context
    if request.user.is_authenticated():
        user_cart, created = Cart.objects.get_or_create(customer=request.user)
        user_cart_details = CartDetails.objects.filter(cart=user_cart)
        context = {
            'user_cart': user_cart,
            'user_cart_details': user_cart_details,
            'key_id': RAZORPAY_KEY_ID,
        }
    else:
        context = {
            'login_form': LoginForm(),
            'signup_form': SignupForm(),
            'forgot_password_form': ForgotPasswordForm(),
            'contact_us_form': ContactUsForm(),
        }

    return context