import time
import threading
import subprocess

from db import init_database
from db.Cameras import add_camera, get_all_cameras

from lib.camfinder import cam_finder
from utils.ffmpeg import ffmpeg_streaming

subnet = "192.168.1.0/24"     # should be presented in CIDR form
rtmp_stream_addr = "rtmp://localhost/live"
frame_width = 640
frame_height = 480


def camera_thread(name, addr):
    input_addr = "rtsp://%s:554/mjpeg/1" % addr
    output_addr = rtmp_stream_addr + "/" + name
    ffmpeg_streaming(input_addr, output_addr)


def init_cameras():
    cameras = get_all_cameras()
    for cam in cameras:
        t = threading.Thread(target=camera_thread, args=(cam.ip, ))
        t.start()


if __name__ == "__main__":
    init_database("data.db")
    cameras = cam_finder(subnet)
    for cam in cameras:
        add_camera(str(cam), str(cam))
    init_cameras()