from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CategoryView, ResultsView, HotelMenuView, UserLoginView, SignUpView

urlpatterns = {
    url(r'^categorys/$', CategoryView.as_view(), name='category'),
    url(r'^results/(?P<pk>[0-9]+)/$', ResultsView.as_view(), name='results'),
    url(r'^hotel/(?P<pk>[0-9]+)/menu$', HotelMenuView.as_view(), name="hotel-menu"),
    url(r'^signup/user$', SignUpView.as_view(), name="signup-user"),
    url(r'^v1/login/$', UserLoginView.as_view(), name='login-user'),

}

urlpatterns = format_suffix_patterns(urlpatterns)