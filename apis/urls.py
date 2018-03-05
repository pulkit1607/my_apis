from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from .views import CategoryView

urlpatterns = {
    url(r'^categorys/$', CategoryView.as_view(), name='category'),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),

}

urlpatterns = format_suffix_patterns(urlpatterns)