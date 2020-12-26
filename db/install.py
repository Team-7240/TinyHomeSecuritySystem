from db import Base, Users, Options, get_engine, get_session
from utils.hash import md5


def setup_database(admin_username: str, admin_password: str) -> bool:
    """
    数据库初始化
    @:param admin_username 管理员用户名
    @:param admin_password 管理员密码
    @:return bool 返回创建结果
    """

    # 创建数据表
    Base.metadata.create_all(get_engine())

    # 写入数据
    session = get_session()
    session.add(Users(username=admin_username,
                      password=md5(admin_password),
                      permission=1))
    session.add(Options(name="installed",
                        value="true"))
    session.add(Options(name="streaming_server",
                        value="rtmp://localhost/live"))
    session.add(Options(name="flv_server",
                        value="http://localhost:5002/live"))
    session.commit()
    session.close()
    return True
