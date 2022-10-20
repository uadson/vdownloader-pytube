from pathlib import Path, PurePosixPath, PureWindowsPath
import os


# Path root
BASE = Path(__file__).resolve().parent.parent

# Path src
SRC_PATH = Path(__file__).resolve().parent

# Path folder media
if os.name == 'nt':
    # windows
    MEDIA_PATH = PureWindowsPath(SRC_PATH).joinpath('media')
else:
    # linux
    MEDIA_PATH = PurePosixPath(SRC_PATH).joinpath('media')

# Path folder video
if os.name == 'nt':
    VIDEO_PATH = PureWindowsPath(MEDIA_PATH).joinpath('video')
else:
    VIDEO_PATH = PurePosixPath(MEDIA_PATH).joinpath('video')

# Folders's resolutions
if os.name == 'nt':
    VD_360_PATH = PureWindowsPath(VIDEO_PATH).joinpath('360')
else:
    VD_360_PATH = PurePosixPath(VIDEO_PATH).joinpath('360')

if os.name == 'nt':
    VD_720_PATH = PureWindowsPath(VIDEO_PATH).joinpath('720')
else:
    VD_720_PATH = PurePosixPath(VIDEO_PATH).joinpath('720')

if os.name == 'nt':
    VD_1080_PATH = PureWindowsPath(VIDEO_PATH).joinpath('1080')
else:
    VD_1080_PATH = PurePosixPath(VIDEO_PATH).joinpath('1080')

if os.name == 'nt':
    VD_HQ_PATH = PureWindowsPath(VIDEO_PATH).joinpath('hq')
else:
    VD_HQ_PATH = PurePosixPath(VIDEO_PATH).joinpath('hq')

# Path folder audio
if os.name == 'nt':
    AUDIO_PATH = PureWindowsPath(MEDIA_PATH).joinpath('audio')
else:
    AUDIO_PATH = PurePosixPath(MEDIA_PATH).joinpath('audio')


if __name__ == '__main__':
    print(BASE)
    print(SRC_PATH)
    print(MEDIA_PATH)
    print(VIDEO_PATH)
    print(VD_360_PATH)
    print(VD_720_PATH)
    print(VD_1080_PATH)
    print(VD_HQ_PATH)
    print(AUDIO_PATH)
