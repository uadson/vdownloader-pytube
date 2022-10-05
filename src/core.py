from pytube import YouTube
from pathlib import Path
import os
import shutil


BASE = Path(__file__).resolve().parent.parent

SRC_PATH = Path(__file__).resolve().parent

def get_url(url):
    try:
        url = YouTube(url)
        return url
    except:
        return None


def get_title(url):
    try:
        data = get_url(url)
        return data.title
    except:
        return None


def download(url, res, resol):
    url = get_url(url)
    if res != 4:
        print('Baixando ...')
        stream = url.streams.get_by_itag(res)
        stream.download()
    elif res == 4:
        print('Baixando ...')
        stream = url.streams.get_highest_resolution()
        stream.download()


def creating_dir():
	path_dir = os.listdir(BASE)
	if not 'media' in path_dir:
		os.mkdir('media')


def search_dir():
    path_dir = os.listdir(SRC_PATH)
    for i in range(len(path_dir)):
        if path_dir[i] == 'media':
            return i

def get_media_folder():
    media_dir = search_dir()
    path_dir = os.listdir(SRC_PATH)
    return path_dir[media_dir]


def moving_video():
    media_dir = get_media_folder()
    videos = os.listdir(SRC_PATH)
    for video in videos:
        if video.endswith('.mp4'):
            shutil.move(video, media_dir)
        else:
            pass


if __name__ == '__main__':
    get_media_folder()
