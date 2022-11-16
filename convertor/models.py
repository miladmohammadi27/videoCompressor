import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from django.db import models
from convertor.dispatcher import ConvertorDispatcher

class Video(models.Model):
    video = models.FileField(upload_to='static/video/',
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])

    name = models.CharField(max_length=100, null=True, blank=True)

    video_720 = models.FileField(upload_to='static/video/', null=True, blank=True,
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])

    video_480 = models.FileField(upload_to='static/video/', null=True, blank=True,
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])

    video_360 = models.FileField(upload_to='static/video/', null=True, blank=True,
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return '{}'.format(self.name)


"""
pre save method to rename the video
"""
@receiver(pre_save, sender=Video)
def rename(sender, instance, *args, **kwargs):
    if not instance.pk:
        video_name = uuid.uuid4()
        instance.name = str(video_name)
        video_extension = instance.video.name.split('.')[-1]
        instance.video.name = f'{video_name}.{video_extension}'


"""
post save method for compress video to lower resolutions
"""
@receiver(post_save, sender=Video)
def convert(sender, instance, created, **kwargs):
    if created:
        """
        prevent to wait until compressing process done
        """
        _thread_pool_cpus = int(os.cpu_count() / 4)
        execute = ThreadPoolExecutor(max_workers=max(_thread_pool_cpus, 1))
        execute.submit(ConvertorDispatcher(instance).dispatch())
