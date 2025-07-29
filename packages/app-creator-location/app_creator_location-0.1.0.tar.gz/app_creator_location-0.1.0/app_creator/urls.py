# app_creator/urls.py

from django.urls import path,include
from .views import get_location_view

urlpatterns = [
    path('ip/', get_location_view, name='get_location'),
]
path('', include('app_creator.urls')),
