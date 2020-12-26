import threading

from flask import Flask
from flask_cors import CORS

from db import init_database, check_install_status
from db.Cameras import get_all_cameras

from lib.streamer import add_camera_thread
from lib.monitor import monitor_all

from router.install import installer
from router.api import api


app = Flask(__name__,
            static_url_path='',
            static_folder='public')
app.register_blueprint(installer)
app.register_blueprint(api)
CORS(app)

data_file = "data.db"
init_database(data_file)
installed = check_install_status()


@app.route('/')
@app.route('/app')
@app.route('/app/<route>')
@app.route('/app/video/<route>')
@app.route('/login')
@app.route('/installer')
def root(route=None):
    return app.send_static_file('index.html')



if installed:
    cameras = get_all_cameras()
    for cam in cameras:
        name = cam.name
        ip = cam.ip
        t = threading.Thread(target=add_camera_thread, args=(name, ip,))
        t.start()
else:
    print("HomeSec is not installed. Consider visit http://127.0.0.1:5000/install to initialize it.")


