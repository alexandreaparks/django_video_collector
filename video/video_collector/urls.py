# URLs for video_collector app - routed here from video.urls.py file

from django.urls import path
from . import views

urlpatterns = [
    # home page url path - requests to this url use home function in views.py file
    path('', views.home, name='home'),
    # url path to add a new video - uses add function in views.py
    path('add', views.add, name='add_video'),
    # url path to view the list of videos
    path('video_list', views.video_list, name='video_list'),
    # url path to a video detail page
    # uses video PK in URL to specify which video to use on detail page
    path('video/<int:video_pk>', views.video_details, name='video_details')

]

