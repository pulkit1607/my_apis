from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (CategoryView, ResultsView, HotelMenuView, UserLoginView, SignUpView,
                    AddToCartView, CartDetailView, ForgetPasswordView, ResetPasswordView,
                    UserOrdersView, UserOrderDetailView, UserDetailView, UserUpdateView,
                    HotelOrdersView)

urlpatterns = {
    url(r'^categorys/$', CategoryView.as_view(), name='category'),
    url(r'^results/(?P<pk>[0-9]+)/$', ResultsView.as_view(), name='results'),
    url(r'^hotel/(?P<pk>[0-9]+)/menu/$', HotelMenuView.as_view(), name="hotel-menu"),
    url(r'^signup/user$', SignUpView.as_view(), name="signup-user"),
    url(r'^v1/login/$', UserLoginView.as_view(), name='login-user'),
    url(r'^v1/add/cart/$', AddToCartView.as_view(), name='add-to-cart'),
    url(r'^v1/cart/details/$', CartDetailView.as_view(), name='cart-details'),
    url(r'^v1/orders/$', UserOrdersView.as_view(), name='user-orders'),
    url(r'^v1/order/booking/(?P<order_id>[0-9]{1,10})/details/$', UserOrderDetailView.as_view(), name='user-order-detail'),
    url(r'^v1/user/details/$', UserDetailView.as_view(), name='user-details'),
    url(r'^v1/user/(?P<pk>[0-9]+)/update/$', UserUpdateView.as_view(), name='user-update'),
    url(r'^v1/forget/password/$', ForgetPasswordView.as_view(), name='forget-password'),
    url(r'^v1/reset-password/(?P<token>\w+)/$', ResetPasswordView.as_view(), name='reset-password'),
    # url(r'^hotel/(?P<pk>[0-9]+)/orders/$', HotelOrdersView.as_view(), name="hotel-menu"),


}

urlpatterns = format_suffix_patterns(urlpatterns)