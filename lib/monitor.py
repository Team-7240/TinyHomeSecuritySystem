import requests
import threading
import time

from db.Cameras import get_all_cameras, get_camera_status, set_camera_status


def get_camera_online_status(address):
    try:
        status = requests.get("http://%s" % address, timeout=3).text
        if "ESP32" in status:
            return True
    except Exception:
        return False
    return True


def monitor_thread(name, address):
    current_status = 1 if get_camera_status(address) == 1 else 0
    while True:
        try:
            current_status = 1
            status = requests.get("http://%s" % address, timeout=1).text
        except Exception:
            print("Camera %s[%s] is down." % (name, address))
            current_status = 0
        if not current_status:
            time.sleep(60)
        else:
            time.sleep(10)


def add_monitor_thread(name, address):
    print("Add monitor thread for %s <%s>" % (name, address))
    t = threading.Thread(target=monitor_thread, args=(name, address, ))
    t.start()


def monitor_all():
    cameras = get_all_cameras()
    for cam in cameras:
        add_monitor_thread(cam.name, cam.ip)
