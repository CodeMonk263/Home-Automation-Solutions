from django.urls import path
from .viewsets import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', AppSerializerViewset, basename='app')
urlpatterns = router.urls