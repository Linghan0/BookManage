# -*- coding: utf-8 -*-
# back/db/user_tools.py

from models import User
from db import DBSession

def authenticate_user(username, password):
    """验证用户凭据"""
    with DBSession() as session:
        user = session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

def get_user_by_id(user_id):
    """根据ID获取用户"""
    with DBSession() as session:
        return session.query(User).get(user_id)

def get_user_by_username(username):
    """根据用户名获取用户"""
    with DBSession() as session:
        return session.query(User).filter_by(username=username).first()

def register_user(username, hashed_password, role='user'):
    """注册新用户
    Args:
        username: 用户名
        hashed_password: 已加密的密码(60字符的bcrypt哈希)
        role: 用户角色(默认为'user')
    Returns:
        User: 新创建的用户对象
    Raises:
        ValueError: 如果用户名已存在或密码格式不正确
    """
    with DBSession() as session:
        # 检查用户名是否已存在
        if get_user_by_username(username):
            raise ValueError('用户名已存在')
            
        # 验证密码格式(64字符的sha256哈希)
        if len(hashed_password) != 64:
            raise ValueError('密码格式不正确，必须是64字符的sha256哈希值')
            
        # 创建新用户
        user = User(username=username, password=hashed_password, role=role)
        session.add(user)
        session.commit()
        return user

def delete_user(username):
    """删除用户
    Args:
        username: 要删除的用户名
    Returns:
        bool: 是否成功删除
    """
    with DBSession() as session:
        user = get_user_by_username(username)
        if not user:
            return False
            
        session.delete(user)
        session.commit()
        return True
