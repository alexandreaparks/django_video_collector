from urllib import parse
from django.core.exceptions import ValidationError
from django.db import models


class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)  # YouTube video url ID - no duplicates allowed

    def save(self, *args, **kwargs):  # override save function

        # validate user enters a YouTube.com url
        if not self.url.startswith('https://www.youtube.com/watch'):
            raise ValidationError(f'Not a YouTube URL {self.url}')

        # extract video_id from YouTube url
        url_components = parse.urlparse(self.url)  # use urllib to break down the url into components
        query_string = url_components.query  # get query string from the url components - 'v=12345678910'
        if not query_string:
            raise ValidationError(f'Invalid YouTube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True)  # dictionary
        v_parameters_list = parameters.get('v')  # returns None if no key found
        if not v_parameters_list:  # if None or empty list
            raise ValidationError(f'Invalid YouTube URL, missing parameters {self.url}')

        # if all validation is passed, declare video_id and save all to DB
        self.video_id = v_parameters_list[0]
        super().save(*args, **kwargs)  # call original save function so that everything is saved to DB

    def __str__(self):  # for development - user will not see this!
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID: {self.video_id}, Notes: {self.notes[:200]}'
