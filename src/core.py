from pytube import YouTube
import moviepy.editor as mp
from storage import (
    VIDEO_PATH, VD_360_PATH, VD_720_PATH, 
    VD_1080_PATH, VD_HQ_PATH, AUDIO_PATH
)
import os
import shutil
import re


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
        return data.description
    except:
        return None


def get_length(url):
    """
        Return length of strema
    """
    try:
        data = get_url(url)
        return data.length
    except:
        return None


def download_video(url, res):
    """
        Download the video according to the resolution chosen by the user
        1 - 360p
        2 - 720p
        3 - 1080p
        4 - HQ - High Quality
    """
    url = get_url(url)
    if res == 1:
        print('Baixando ...')
        stream = url.streams.get_by_itag(18)
        stream.download(output_path=VD_360_PATH)
    elif res == 2:
        print('Baixando ...')
        stream = url.streams.get_by_itag(22)
        stream.download(output_path=VD_720_PATH)
    elif res == 3:
        print('Baixando ...')
        stream = url.streams.get_by_itag(137)
        stream.download(output_path=VD_1080_PATH)       
    elif res == 4:
        print('Baixando ...')
        stream = url.streams.get_highest_resolution()
        stream.download(output_path=VD_HQ_PATH)


def download_audio(url):
    print('Baixando ...')
    url = get_url(url)
    audio = url.streams.filter(only_audio=True).first().download(AUDIO_PATH)
    for file in os.listdir(AUDIO_PATH):
        if re.search('mp4', file):
            mp4_path = os.path.join(AUDIO_PATH, file)
            mp3_path = os.path.join(AUDIO_PATH, os.path.splitext(file)[0] + '.mp3')
            new_file = mp.AudioFileClip(mp4_path)
            new_file.write_audiofile(mp3_path)
            os.remove(mp4_path)


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
