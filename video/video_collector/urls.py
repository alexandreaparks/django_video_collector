# URLs for video_collector app - routed here from video.urls.py file

from django.urls import path
from . import views

urlpatterns = [
    # home page url path - requests to this url use home function in views.py file
    path('', views.home, name='home'),
]

