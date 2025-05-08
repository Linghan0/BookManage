# -*- coding: utf-8 -*-
# back/db/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

def get_engine():
    """获取数据库引擎"""
    # 从环境变量获取数据库URL，必须配置
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError('DATABASE_URL must be configured in .env file')
    return create_engine(
        db_url,
        echo=os.getenv('DB_ECHO', 'false').lower() == 'true',
        connect_args={'check_same_thread': os.getenv('DB_CHECK_SAME_THREAD', 'false').lower() == 'true'},
        isolation_level=os.getenv('DB_ISOLATION_LEVEL', 'SERIALIZABLE')
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
