from django.test import TestCase
from . import models


class TestVideoModel(TestCase):

    def test_save_video(self):
        with open('testVideo/1_720.mp4') as file:
            print(file)
            video = models.Video.objects.create(
                video=file,
            )
