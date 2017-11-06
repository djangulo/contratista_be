from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from accounts.api import (
    throttled_obtain_token,
    UserViewSet,
    RegisterUserViewSet
)
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'register', RegisterUserViewSet, base_name='register')
# router.register(r'my_viewset', MyViewSet)

urlpatterns = [
    url(r'^api/v1/', throttled_obtain_token, name='get-token'),
    url(r'^api/v1/', include(router.urls)),  
]
