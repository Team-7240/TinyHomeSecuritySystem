import time
import threading
import requests
import subprocess

from db import init_database
from db.Cameras import add_camera, get_all_cameras, set_camera_status
from db.Option import get_options_by_name

from lib.camfinder import cam_finder
from utils.ffmpeg import ffmpeg_streaming


frame_width = 640
frame_height = 480

threads_pool = {}


def camera_thread(name, addr):
    rtmp_stream_addr = get_options_by_name("streaming_server")
    input_addr = "rtsp://%s:554/mjpeg/1" % addr
    output_addr = rtmp_stream_addr + "/" + name
    ffmpeg_streaming(input_addr, output_addr)


def add_camera_thread(name, addr):
    global threads_pool
    try:
        status = requests.get("http://%s" % addr,  timeout=3).text
        if "ESP32" in status:
            threads_pool[name] = threading.Thread(target=camera_thread, args=(name, addr, ))
            threads_pool[name].start()
        else:
            raise KeyError
    except Exception:
        print("Cannot establish a connection with %s. This camera may be down." % (addr))


