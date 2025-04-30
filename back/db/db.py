# -*- coding: utf-8 -*-
# back/db/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config import DB_PATH

def get_engine():
    """获取数据库引擎"""
    # 将Path对象转换为字符串，并确保使用正斜杠
    db_path_str = str(DB_PATH).replace('\\', '/')
    return create_engine(
        f'sqlite:///{db_path_str}',
        echo=True,
        connect_args={'check_same_thread': False},
        isolation_level='SERIALIZABLE'
    )

def init_db():
    """初始化数据库"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """获取数据库会话"""
    engine = get_engine()
    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False
    )
    return Session()

class DBSession:
    """数据库会话上下文管理器"""
    def __init__(self):
        self.session = get_session()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
