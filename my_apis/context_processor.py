from django.shortcuts import render, redirect, get_object_or_404
from apis.forms import LoginForm, SignupForm, ForgotPasswordForm
from apis.models import Cart, CartDetails

def form_context(request):
    # pass the login, signup and forgot password form in all pages as a context
    if request.user.is_authenticated():
        user_cart = Cart.objects.get_or_create(customer=request.user)
        user_cart_details = CartDetails.objects.filter(cart=user_cart[0])
        context = {
            'user_cart': user_cart,
            'user_cart_details': user_cart_details,
        }
    else:
        context = {
            'login_form': LoginForm(),
            'signup_form': SignupForm(),
            'forgot_password_form': ForgotPasswordForm(),
        }

    return context