"""my_apis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from apis.views import *
from django.conf import settings
from django.conf.urls.static import static

from my_apis.schema_generator import get_swagger_view

schema_view = get_swagger_view(title='FINGERTIPS API')


urlpatterns = [
    url(r'^admin/thequeuedteam/', admin.site.urls),
    url(r'^', include('apis.urls')),
    url(r'^api-docs/', schema_view),
    url(r'^$', HomeView.as_view(), name='home'),
    # url(r'^hotel/(?P<pk>[0-9]+)/dashboard/$', DashBoardView.as_view(), name='dashboard-view'),
    url(r'^hotel/dashboard/$', DashBoardView.as_view(), name='dashboard-view'),
    url(r'^vendor/login/$', VendorLoginView.as_view(), name='vendor-login-view'),
    url(r'^vendor/logout/$', VendorLogoutView.as_view(), name='vendor-logout'),
    url(r'^order/(?P<pk>[0-9]+)/details/$', CustomerOrderDetails.as_view(), name='customer-order-details'),
    # url(r'^vendor/(?P<pk>[0-9]+)/menu/$', VendorMenuView.as_view(), name='vendor-menu-view'),
    url(r'^vendor/menu/$', VendorMenuView.as_view(), name='vendor-menu-view'),
    url(r'^vendor/location/$', VendorLocationListView.as_view(), name='vendor-location-list'),
    url(r'^vendor/location/add/$', VendorLocationAddView.as_view(), name='vendor-add-location'),
    url(r'^vendor/location/(?P<pk>[0-9]+)/update/$', VendorLocationUpdateView.as_view(), name='vendor-update-location'),
    url(r'^vendor/menu/upload/$', VendorMenuUploadView.as_view(), name='vendor-menu-upload'),
    url(r'^vendor/orders/list/$', VendorOrderListView.as_view(), name='vendor-orders-list'),
    url(r'^verify-payment/$',VerifyPaymentView.as_view(), name='verify_payment'),
    url(r'^list-restaurants/$', RestaurantListView.as_view(), name='list-all-restaurant'),
    url(r'^restaurant/(?P<pk>[0-9]+)/menu/$', RestaurantMenuView.as_view(), name='restaurant-menu-view'),
    url(r'^account/login/$', LoginView.as_view(), name="login-user"),
    url(r'^account/logout/$', LogoutView.as_view(), name='logout-user'),
    url(r'^account/signup/$', SignupView.as_view(), name="signup-user"),
    url(r'^contact/$', ContactView.as_view(), name="contact"),
    url(r'^account/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        EmailAccountActivate.as_view(), name='activate'),
    url(r'^account/forgot-password/$', ForgotPasswrod.as_view(), name="forgot-password"),
    url(r'^account/reset-password/(?P<token>\w+)/$', ResetPasswordView.as_view(), name='reset-password'),
    url(r'^user/cart/details/$', UserCartView.as_view(), name='user-cart'),
    url(r'^add/to/cart/$', AddCartView.as_view(), name='add-cart-view'),
    url(r'^dec/to/cart/$', DecrementCartView.as_view(), name='dec-cart-view'),
    url(r'^clear/cart/$', ClearCartView.as_view(), name='clear-cart'),
    url(r'^order/now/$', OrderNowView.as_view(), name='order-now'),
    url(r'^create/order/pay/now/$', CreateOrderView.as_view(), name='create-order'),
    url(r'^create/order/pay/hotel/$', CreateOrderPayHotelView.as_view(), name='create-order-pay-hotel'),
    url(r'^profile/update/$', ProfileUpdateView.as_view(), name='update-profile'),
    url(r'^orders/list/$', OrdersListView.as_view(), name='orders-list'),
    url(r'^order/detail/(?P<pk>[0-9]+)/$', OrderDetailView.as_view(), name='orders-detail'),
    url(r'^order/confirmation/(?P<order_id>[0-9]{1,10})/$', OrderConfirmationView.as_view(), name='order-confirmation'),
    url(r'^order/confirmation/instamojo/$', InstamojoOrderConfirmationView.as_view(), name='instamojo-order-confirmation'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
