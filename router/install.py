from flask import Blueprint, request

from db import check_install_status
from db.install import setup_database

installer = Blueprint("installer", __name__, url_prefix="/install")


@installer.route("/status")
def get_install_status():
    return {
        "code": 200,
        "status": "success",
        "installed": check_install_status()
    }


@installer.route("/install", methods=["POST"])
def install():
    if check_install_status():
        return {
            "code": 403,
            "status": "failed",
            "info": "Database already installed / initialized."
        }

    admin_username = request.form.get("admin_username")
    admin_password = request.form.get("admin_password")

    if not admin_username or not admin_password:
        return {
            "code": 400,
            "status": "failed",
            "info": "requested field can not be empty."
        }

    status = setup_database(admin_username, admin_password)

    if status:
        return {
            "code": 200,
            "status": "success",
            "info": "System installed."
        }
    else:
        return {
            "code": 500,
            "status": "failed",
            "info": "internal system error."
        }
