from django.urls import path,include

from barDetails import views
from rest_framework import routers

from rest_framework.routers import DefaultRouter

# Use Viewsets
router = DefaultRouter()
router = routers.DefaultRouter(trailing_slash=False)

# Bares
router.register('barDetalles', views.BarDetallesViewSet)


app_name = 'barDetails'

urlpatterns = [
    path('',include(router.urls))
]