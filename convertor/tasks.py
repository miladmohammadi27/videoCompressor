from json import loads
from subprocess import Popen, PIPE
from celery import shared_task
from django.shortcuts import get_object_or_404

from . import models


"""
gets new created video and returns resolution
"""
@shared_task
def get_resolution(video_url):

    command = ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
        "stream=width,height", "-of", "json", f"{video_url}"]

    with Popen(command, stdout=PIPE, universal_newlines=True) as process:
        response = loads(process.stdout.read())
        response['return_code'] = process.returncode

    return response


"""
convert video to lower resolutions
"""
@shared_task
def convert_resolution(video_url, requested_resolution, video_name, video_type, save_path):
    response: map = {}

    if requested_resolution == "1080":
        output_resolution = {"width": "1920", "height": "1080"}
    elif requested_resolution == "720":
        output_resolution = {"width": "1280", "height": "720"}
    elif requested_resolution == "480":
        output_resolution = {"width": "854", "height": "480"}
    elif requested_resolution == "360":
        output_resolution = {"width": "640", "height": "360"}
    elif requested_resolution == "240":
        output_resolution = {"width": "426", "height": "240"}
    else:
        return ({
            "status": "failed",
            "message": "We Can't Convert To This Resolution"
        })

    command = ["ffmpeg", "-i", f"{video_url}", "-vf",
               f"scale={output_resolution['width']}:{output_resolution['height']}", "-vcodec", "libx265", "-crf", "28",
               "-c:a", "copy", f"{save_path}/{video_name}_{requested_resolution}p.{video_type}"]

    with Popen(command, stdout=PIPE, universal_newlines=True) as process:

        if process.returncode is None:
            video = get_object_or_404(models.Video, name=video_name)

            if requested_resolution == '720':
                with open(f"/code/static/video/{save_path}/{video_name}_{requested_resolution}p.{video_type}") as file:
                    video.video_720 = file
            elif requested_resolution == '480':
                with open(f"/code/static/video/{save_path}/{video_name}_{requested_resolution}p.{video_type}") as file:
                    video.video_480 = file
            elif requested_resolution == '360':
                with open(f"/code/{save_path}/{video_name}_{requested_resolution}p.{video_type}") as file:
                    print(file)
                    print("%%%"*20)
                    video.video_360 = file

            video.save()

            response['status'] = "success"
            response['message'] = "Video Converted Successfully"
            response['response'] = process.stdout.read()
            response['return_code'] = process.returncode
        else:
            response['status'] = "failed"
            response['response'] = "Something Went Wrong - Check Parameters"
            response['return_code'] = process.returncode

    return response

