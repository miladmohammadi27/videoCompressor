from convertor.tasks import get_resolution, convert_resolution
from celery import group


"""
convertor dispatcher gets new created video instance and checks video resolution
then calls compress task for compressing video to lower resolutions
for example if video resolution is 1080p dispatcher send tasks fo converting it to 
720p , 480p, 360p
"""
class ConvertorDispatcher:
    def __init__(self, video):
        self.video_url = str(video.video)
        self.video_type, self.video_name = str(video.video).split('.')[-1], str(video.video).split('.')[0]
        self.video_name = self.video_name.split('/')[-1]
        self.save_path = 'static/video'

    def dispatch(self):
        video_resolution = self._get_video_resolution()['streams'][0]['height']
        convert_to = []

        if video_resolution == 1080:
            convert_to: list = ['720', '480', '360']
        if video_resolution == 720:
            convert_to: list = ['480', '360']
        if video_resolution == 480:
            convert_to: list = ['360']

        self._compress(convert_to)

    def _get_video_resolution(self):
        video_resolution = get_resolution.delay(f'http://video_compressor_django:8000/{self.video_url}')
        return video_resolution.get()

    def _compress(self, convert_to: list):
        compress_tasks = []
        for resolution in convert_to:

            compress_tasks.append(
                convert_resolution.signature((
                    self.video_url,
                    resolution,
                    self.video_name,
                    self.video_type,
                    self.save_path
                ))
            )

        result = group(*compress_tasks).apply_async()
        print(result)




