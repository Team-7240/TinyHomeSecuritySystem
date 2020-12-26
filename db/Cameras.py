from db import Cameras, get_session


def remove_camera(index):
    session = get_session()
    session.query(Cameras).filter(Cameras.id == index).delete()
    session.commit()
    session.close()
    return True


def get_all_cameras():
    session = get_session()
    result = session.query(Cameras).all()
    session.close()
    return result


def get_camera(target):
    session = get_session()
    result = session.query(Cameras).filter(Cameras.id == target or Cameras.ip == target or Cameras.name == target).first()
    session.close()
    return result


def set_camera_status(address, status):
    session = get_session()
    print(session.query(Cameras).filter(Cameras.ip == address).first())
    session.query(Cameras).filter(Cameras.ip == address).update({"status", status})
    session.commit()
    session.close()


def get_camera_status(address):
    cam = get_camera(address)
    if not cam:
        return 0
    return cam.status


def add_camera(name, ip):
    session = get_session()

    # 已存在相同 IP 的摄像头
    query = session.query(Cameras).filter(Cameras.ip == ip).all()
    if len(query):
        return False

    session.add(Cameras(name=name, ip=ip))
    session.commit()
    session.close()
    return True
