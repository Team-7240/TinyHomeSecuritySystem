import requests
import threading
import time

from IPy import IP

cams = []
count = 0


# 向指定地址发送 get 请求，判断是否为 esp32 摄像头模组
def send_request(address, begin, end):
    for i in range(begin, min(end, len(address))):
        try:
            addr = address[i]
            payload = requests.get("http://%s" % addr, timeout=0.5).text
            if "ESP32CAM" in payload:
                cams.append(addr)
        except Exception as e:
            pass
    global count
    count += 1          # 线程退出计数


# 在指定的局域网内寻找 esp32 摄像头；使用多线程加快查找速度
def cam_finder(subnet, batch=5):
    addresses = IP(subnet)
    global cams
    global count
    cams = []
    count = 0
    total = len(addresses)
    threads = 0
    index = 0
    # 多线程扫描局域网内的摄像头
    while index < total:
        t = threading.Thread(target=send_request, args=(addresses, index, min(index + batch, total)))
        t.start()
        index = index + batch
        threads += 1
    while True:
        time.sleep(1)
        if count == threads:
            return cams


# test
if __name__ == "__main__":
    print(cam_finder("192.168.1.0/24"))
