from django import forms
from .models import Video


class VideoForm(forms.ModelForm):
    # use Video model to create a form with the fields name, url, and notes
    class Meta:
        model = Video
        fields = ['name', 'url', 'notes']


class SearchForm(forms.Form):  # form used to get search term from user
    search_term = forms.CharField()
