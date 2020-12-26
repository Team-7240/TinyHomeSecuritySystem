import datetime
import socket

from flask import Blueprint, request
from wtforms import Form, StringField, IntegerField, validators

from lib.camfinder import cam_finder
from lib.streamer import add_camera_thread
from lib.monitor import get_camera_online_status

from db.Users import get_user_by_id, get_user_by_name, update_auth_key, add_user, get_all_users, delete_user
from db.Cameras import add_camera, get_all_cameras, remove_camera
from db.Option import get_options_by_name, set_option

from utils.hash import md5


api = Blueprint("api", __name__, url_prefix="/api")


# 用户登录 API
@api.route("/user/login", methods=["POST"])
def login():
    class UserLoginForm(Form):
        username = StringField("username", [ validators.DataRequired() ])
        password = StringField("password", [ validators.DataRequired() ])
    form = UserLoginForm(request.form, csrf_enabled=False)

    if form.validate():
        user = get_user_by_name(form.username.data)
        if len(user) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        password = md5(form.password.data)
        if user[0].password != password:
            return {
                "code": 403,
                "status": "failed",
                "info": "password is incorrect."
            }
        auth_key = md5("%s-%s-%s" % (user[0].username, user[0].password, str(datetime.datetime.now().timestamp())))
        update_auth_key(user[0].id, auth_key)
        return {
            "code": 200,
            "status": "success",
            "info": "login successfully.",
            "authKey": auth_key,
            "uid": user[0].id
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 摄像头扫描 API
@api.route("/camera/scan", methods=["POST"])
def scan_camera():
    class ScanCameraForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        subnet = StringField("subnet", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
    form = ScanCameraForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data or users[0].permission < 1:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        cameras = cam_finder(form.subnet.data)
        results = []
        for cam in cameras:
            results.append(str(cam))
        return {
            "code": 200,
            "status": "success",
            "payload": results
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 摄像头添加 API
@api.route("/camera/add", methods=["POST"])
def add_camera_api():
    class AddCameraForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        name = StringField("name", [ validators.DataRequired() ])
        ip = StringField("ip", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
    form = AddCameraForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data or users[0].permission < 1:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        res = add_camera(form.name.data, form.ip.data)
        add_camera_thread(form.name.data, form.ip.data)
        return {
            "code": 200,
            "status": "success" if res else "failed"
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 获取摄像头 API
@api.route("/camera/get", methods=["POST"])
def get_camera_api():
    class GetCameraForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
    form = GetCameraForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        result = []
        cameras = get_all_cameras()
        for cam in cameras:
            result.append({
                "id": cam.id,
                "name": cam.name,
                "ip": cam.ip
            })
        return {
            "code": 200,
            "status": "success",
            "payload": result
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 添加用户 API
@api.route("/users/add", methods=["POST"])
def add_users_api():
    class AddUsersForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
        username = StringField("username", [ validators.DataRequired() ])
        password = StringField("password", [ validators.DataRequired() ])
        permission = StringField("permission", [ validators.InputRequired() ])
    form = AddUsersForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data or users[0].permission < 1:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        status = add_user(form.username.data,
                          form.password.data,
                          form.permission.data)
        return {
            "code": 200,
            "status": "success" if status else "failed"
        }
    else:
        print(form.errors)
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 删除用户 API
@api.route("/users/delete", methods=["POST"])
def delete_users_api():
    class DelUsersForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
        target = IntegerField("target", [ validators.DataRequired() ])
    form = DelUsersForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        target_user = get_user_by_id(form.target.data)
        if len(users) == 0 or len(target_user) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data or users[0].permission < 1 or users[0].permission <= target_user[0].permission:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        status = delete_user(form.target.data)
        return {
            "code": 200,
            "status": "success" if status else "failed"
        }
    else:
        print(form.errors)
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 获取全部用户 API
@api.route("/users/all", methods=["POST"])
def get_all_users_api():
    class GetAllUsersForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
    form = GetAllUsersForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        total = get_all_users()
        results = []
        for user in total:
            results.append({
                "uid": user.id,
                "username": user.username,
                "permission": user.permission
            })
        return {
            "code": 200,
            "status": "success",
            "payload": results
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 设置选项 API
@api.route("/option/set", methods=["POST"])
def set_option_api():
    class SetOptionForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
        name = StringField("name", [ validators.DataRequired() ])
        value = StringField("value", [ validators.DataRequired() ])
    form = SetOptionForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data or users[0].permission < 1:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        status = set_option(name=form.name.data, value=form.value.data)
        return {
            "code": 200,
            "status": "success" if status else "failed"
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 获取选项 API
@api.route("/option/get", methods=["POST"])
def get_option_api():
    class GetOptionForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
        name = StringField("name", [ validators.DataRequired() ])
    form = GetOptionForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        value = get_options_by_name(name=form.name.data)
        return {
            "code": 200,
            "status": "success",
            "value": value
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 用户 authKey 验证
@api.route("/users/verify", methods=["POST"])
def verify():
    class VerifyForm(Form):
        uid = StringField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
    form = VerifyForm(request.form, csrf_enabled=False)

    if form.validate():
        user = get_user_by_id(form.uid.data)
        if len(user) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if user[0].authKey != form.authKey.data:
            return {
                "code": 403,
                "status": "failed",
                "info": "authKey is incorrect."
            }
        return {
            "code": 200,
            "status": "success",
            "info": "identity verified."
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 获取用户信息
@api.route("/users/info", methods=["POST"])
def userinfo():
    class UserInfoForm(Form):
        uid = StringField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
    form = UserInfoForm(request.form, csrf_enabled=False)

    if form.validate():
        user = get_user_by_id(form.uid.data)
        if len(user) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if user[0].authKey != form.authKey.data:
            return {
                "code": 403,
                "status": "failed",
                "info": "authKey is incorrect."
            }
        user_info = get_user_by_id(form.uid.data)
        payload = {
            "name": user_info[0].username,
            "uid": user_info[0].id,
            "permission": user_info[0].permission
        }
        return {
            "code": 200,
            "status": "success",
            "payload": payload
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 获取摄像头的状态
@api.route("/camera/status", methods=["POST"])
def get_camera_status_api():
    class GetCameraStatusForm(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
        address = StringField("address", [ validators.DataRequired() ])
    form = GetCameraStatusForm(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        status = get_camera_online_status(form.address.data)
        return {
            "code": 200,
            "status": "success",
            "online": status
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }


# 摄像头删除 API
@api.route("/camera/delete", methods=["POST"])
def delete_camera_api():
    class DeleteCameraAPI(Form):
        uid = IntegerField("uid", [ validators.DataRequired() ])
        authKey = StringField("authKey", [ validators.DataRequired() ])
        target = IntegerField("target", [ validators.DataRequired() ])
    form = DeleteCameraAPI(request.form, csrf_enabled=False)
    if form.validate():
        users = get_user_by_id(form.uid.data)
        if len(users) == 0:
            return {
                "code": 404,
                "status": "failed",
                "info": "user not found."
            }
        if users[0].authKey != form.authKey.data or users[0].permission < 1:
            return {
                "code": 403,
                "status": "failed",
                "info": "permission denied."
            }
        res = remove_camera(form.target.data)
        return {
            "code": 200,
            "status": "success" if res else "failed"
        }
    else:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty"
        }