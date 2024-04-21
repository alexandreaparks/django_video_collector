from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .forms import VideoForm
from .models import Video


def home(request):  # handles requests to home page
    app_name = 'Cat Videos'  # create video app name to use in template
    # render - retrieve data based on parameters, load template, and render/combine template with retrieved data
    return render(request, 'video_collector/home.html', {'app_name': app_name})


def add(request):  # handles requests to the add page

    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():  # uses DB constraints
            try:
                new_video_form.save()  # save to DB
                return redirect('video_list')  # redirect to video_list page
                # messages.info(request, 'New video saved!')

            except ValidationError:  # not a YouTube URL
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:  # duplicate video being added
                messages.warning(request, 'You already added that video!')

        # if not valid, reload same page and form with data already entered by user so user can edit
        messages.warning(request, 'Please check the data entered')
        return render(request, 'video_collector/add.html', {'new_video_form': new_video_form})

    new_video_form = VideoForm()  # create a new video form to use on webpage
    # combine template with form to create webpage
    return render(request, 'video_collector/add.html', {'new_video_form': new_video_form})


def video_list(request):
    videos = Video.objects.all()  # get all the videos saved in the DB
    return render(request, 'video_collector/video_list.html', {'videos': videos})
