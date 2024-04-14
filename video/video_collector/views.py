from django.shortcuts import render


def home(request):
    app_name = 'Cat Videos'  # create video app name to use in template
    # render - retrieve data based on parameters, load template, and render/combine template with retrieved data
    return render(request, 'video_collector/home.html', {'app_name': app_name})
