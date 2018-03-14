from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from .views import CategoryView, ResultsView, HotelMenuView

urlpatterns = {
    url(r'^categorys/$', CategoryView.as_view(), name='category'),
    url(r'^results/(?P<pk>[0-9]+)/$', ResultsView.as_view(), name='results'),
    url(r'^hotel/(?P<pk>[0-9]+)/menu$', HotelMenuView.as_view(), name="hotel-menu"),
    # url(r'^api-token-auth/', obtain_jwt_token),
    # url(r'^api-token-verify/', verify_jwt_token),

}

urlpatterns = format_suffix_patterns(urlpatterns)