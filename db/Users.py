from db import Users, get_session
from utils.hash import md5


def get_user_by_id(uid):
    session = get_session()
    user = session.query(Users).filter(Users.id == uid).all()
    session.close()
    return user


def get_user_by_name(username):
    session = get_session()
    user = session.query(Users).filter(Users.username == username).all()
    session.close()
    return user


def get_all_users():
    session = get_session()
    user = session.query(Users).all()
    session.close()
    return user


def add_user(username, password, permission = 0) -> bool:
    exists = get_user_by_name(username)
    session = get_session()
    if exists:
        session.close()
        return False

    session.add(Users(username=username,
                      password=md5(password),
                      permission=permission))
    session.commit()
    session.close()

    return True


def delete_user(uid) -> bool:
    session = get_session()
    session.query(Users).filter(Users.id == uid).delete()
    session.commit()
    session.close()
    return True


def update_auth_key(uid, auth_key) -> bool:
    session = get_session()
    session.query(Users).filter(Users.id == uid).update({"authKey": auth_key})
    session.commit()
    session.close()
    return True
