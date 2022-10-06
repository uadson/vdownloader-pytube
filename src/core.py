from pytube import YouTube
from pathlib import Path, PurePosixPath, PureWindowsPath
import os
import shutil


BASE = Path(__file__).resolve().parent.parent

SRC_PATH = Path(__file__).resolve().parent

if os.name == 'nt':
    MEDIA_PATH = PureWindowsPath(SRC_PATH).joinpath('media')
else:
    MEDIA_PATH = PurePosixPath(SRC_PATH).joinpath('media')

if os.name == 'nt':
    VIDEO_PATH = PureWindowsPath(MEDIA_PATH).joinpath('video')
else:
    VIDEO_PATH = PurePosixPath(MEDIA_PATH).joinpath('video')

if os.name == 'nt':
    AUDIO_PATH = PureWindowsPath(MEDIA_PATH).joinpath('audio')
else:
    AUDIO_PATH = PurePosixPath(MEDIA_PATH).joinpath('audio')


def get_url(url):
    """
        Get url typed by user
    """
    try:
        url = YouTube(url)
        return url
    except:
        return None


def get_title(url):
    """
        Return title of stream
    """
    try:
        data = get_url(url)
        return data.title
    except:
        return None


def get_desc(url):
    """
        Return description of stream
    """
    try:
        data = get_url(url)
        return data.streams.desc()
    except:
        return None


def download(url, res, resol):
    """
        Download the video according to the resolution chosen by the user
    """
    url = get_url(url)
    if res != 4:
        print('Baixando ...')
        stream = url.streams.get_by_itag(res)
        stream.download()
    elif res == 4:
        print('Baixando ...')
        stream = url.streams.get_highest_resolution()
        stream.download()


def search_media_dir():
    """
        Getting folder media's index
    """         
    path_dir = os.listdir(SRC_PATH)
    for i in range(len(path_dir)):
        if path_dir[i] == 'media':
            return i


def get_media_folder():
    """
        Getting folder media
    """
    media_dir = search_media_dir()
    path_dir = os.listdir(SRC_PATH)
    return path_dir[media_dir]


def get_video_folder():
    path_dir = os.listdir()


def moving_video():
    path = os.listdir(BASE)
    print(path)
    for video in path:
        if video.endswith('.mp4'):
            shutil.move(video, VIDEO_PATH)
        else:
            pass


def movin_audio():
    ...


if __name__ == "__main__":
    ...
