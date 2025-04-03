# -*- coding: utf-8 -*-
# back/db/user_tools.py

from sqlalchemy.orm import sessionmaker
from back.models import User
from back.config import DB_PATH
import sqlite3

def get_db_session():
    """获取数据库会话"""
    engine = sqlite3.connect(str(DB_PATH))
    Session = sessionmaker(bind=engine)
    return Session()

def authenticate_user(username, password):
    """验证用户凭据"""
    session = get_db_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
    finally:
        session.close()

def get_user_by_id(user_id):
    """根据ID获取用户"""
    session = get_db_session()
    try:
        return session.query(User).get(user_id)
    finally:
        session.close()

def get_user_by_username(username):
    """根据用户名获取用户"""
    session = get_db_session()
    try:
        return session.query(User).filter_by(username=username).first()
    finally:
        session.close()
