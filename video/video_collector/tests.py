from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        # make request to homepage
        url = reverse('home')
        response = self.client.get(url)

        # make assertion about the response
        self.assertContains(response, 'Cat Videos')


class TestAddVideos(TestCase):

    def test_add_video(self):
        valid_video = {
            'name': 'cats',
            'url': 'https://www.youtube.com/watch?v=PzF1TuzyTdY',
            'notes': 'so cute!'
        }

        # make POST request to add_video page
        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)  # follow=True - follow the redirect

        # make assertions about response

        # assert video_list template is used when adding video
        self.assertTemplateUsed('video_collector/video_list.html')

        # assert video list shows new video
        self.assertContains(response, 'cats')
        self.assertContains(response, 'so cute!')
        self.assertContains(response, 'https://www.youtube.com/watch?v=PzF1TuzyTdY')

        # assert DB has 1 video
        video_count = Video.objects.count()  # query DB to get count of Video objects
        self.assertEqual(1, video_count)

        # assert Video data in DB matches valid_video data
        video = Video.objects.first()  # get first Video object in DB
        self.assertEqual('cats', video.name)
        self.assertEqual('so cute!', video.notes)
        self.assertEqual('https://www.youtube.com/watch?v=PzF1TuzyTdY', video.url)
        self.assertEqual('PzF1TuzyTdY', video.video_id)

    def test_add_video_invalid_url_not_added(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=123456'
        ]

        # loop over all invalid urls and try to add them
        for invalid_video_url in invalid_video_urls:

            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)

            # assert correct template is used
            self.assertTemplateUsed('video_collector/add.html')

            # assert correct messages are displayed
            messages = response.context['messages']
            message_text = [ message.message for message in messages]

            self.assertIn('Invalid YouTube URL', message_text)
            self.assertIn('Please check the data entered', message_text)

            # assert Video object count in DB is 0
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):

    def test_all_videos_displayed_in_correct_order(self):
        # create 4 example videos
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=125')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=126')

        expected_video_order = [ v3, v2, v4, v1 ]

        url = reverse('video_list')
        response = self.client.get(url)

        # context - the dictionary of data used to render a webpage
        videos_in_template = list(response.context['videos'])  # convert from QuerySet to a list

        self.assertEqual(videos_in_template, expected_video_order)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(response.context['videos']))  # assert 0 videos are sent in context

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')

        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_three_video(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=125')

        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '3 videos')


class TestVideoSearch(TestCase):
    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = []  # empty list
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')


class TestVideoModel(TestCase):

    def test_invalid_url_raises_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=123456',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            '12345678',
            'hhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=123456',
            'https://github.com',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=123456'
        ]

        # try to add each invalid url and assert it raises a Validation Error
        for invalid_video_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_video_url, notes='example notes')

        self.assertEqual(0, Video.objects.count())  # assert no videos are in DB

    def test_duplicate_video_raises_integrity_error(self):
        # add same video two times and assert that it raises an Integrity Error
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')


class TestVideoDetail(TestCase):

    def test_video_exists_details_displayed(self):
        # add test video to DB
        example_video = Video.objects.create(pk=1, name='Cats', notes='So cute!', url='https://www.youtube.com/watch?v=123')

        # make request
        response = self.client.get(reverse('video_details', kwargs={'video_pk': 1}))

        # assert correct template is used
        self.assertTemplateUsed(response, 'video_collector/video_detail.html')

        # assert page contains details about video
        self.assertContains(response, 'Cats')
        self.assertContains(response, 'So cute!')
        self.assertContains(response, 'https://www.youtube.com/watch?v=123')

    def test_video_does_not_exist_returns_404_status(self):
        # make request to view details about video that does not exist
        response = self.client.get(reverse('video_details', kwargs={'video_pk': 12345678}))

        # assert 404 status is returned
        self.assertEqual(404, response.status_code)

