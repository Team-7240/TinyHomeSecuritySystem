import datetime
import os

from sqlalchemy import create_engine, Column, Integer, Text, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.hash import md5

engine = None
Session = None
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32))
    password = Column(String(32))
    register = Column(DateTime, default=datetime.datetime.now)
    permission = Column(Integer)
    authKey = Column(Text)


class Cameras(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(28))
    ip = Column(String(28))
    status = Column(Integer, default=0)     # 0: offline, 1: online


class Options(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    value = Column(Text)


# 初始化数据库
def init_database(sqlite_file):
    global engine
    global Session

    engine = create_engine("sqlite:///%s?check_same_thread=False" % sqlite_file, echo=False)
    Session = sessionmaker(bind=engine)


# 获取数据库安装状态
def check_install_status() -> bool:
    global Session
    session = Session()
    initialized = True
    try:
        installed = session.query(Options).filter(Options.name == "installed").all()
        if len(installed) == 0:
            initialized = False
    except Exception:
        initialized = False
    return initialized


# 获取数据库实例
def get_engine():
    global engine
    return engine


# 获取数据库会话
def get_session():
    global Session
    return Session()
