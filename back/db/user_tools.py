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
        hashed_password: 已加密的密码(64字符的sha256哈希)
        role: 用户角色(默认为'user')
    Returns:
        User: 新创建的用户对象
    Raises:
        dict: 包含详细错误信息的字典，格式为:
            {
                'type': 'validation_error|database_error',
                'message': '详细错误信息',
                'field': '导致错误的字段名(可选)'
            }
    """
    try:
        # 验证用户名长度
        if len(username) < 4 or len(username) > 20:
            return {
                'type': 'validation_error',
                'message': '用户名长度必须在4-20个字符之间',
                'field': 'username'
            }
            
        # 验证角色
        if role not in ('admin', 'user'):
            return {
                'type': 'validation_error',
                'message': '角色只能是admin或user',
                'field': 'role'
            }
            
        with DBSession() as session:
            # 检查用户名是否已存在
            existing_user = get_user_by_username(username)
            if existing_user:
                return {
                    'type': 'database_error',
                    'message': '用户名已存在',
                    'field': 'username'
                }
            
            # 创建新用户
            user = User(username=username, password=hashed_password, role=role)
            session.add(user)
            
            try:
                session.commit()
                session.refresh(user)
                if user in session:
                    return user
                else:
                    # 重新查询确保返回有效用户对象
                    return session.query(User).get(user.user_id)
            except Exception as commit_error:
                print(f"提交失败: {str(commit_error)}")
                session.rollback()
                print("事务已回滚")
                
                # 检查是否是唯一约束违反
                if "UNIQUE constraint failed" in str(commit_error):
                    return {
                        'type': 'database_error',
                        'message': '用户名已存在',
                        'field': 'username'
                    }
                
                return {
                    'type': 'database_error',
                    'message': f'数据库提交错误: {str(commit_error)}'
                }
            
    except Exception as e:
        print(f"注册过程中发生异常: {str(e)}")
        return {
            'type': 'database_error',
            'message': f'数据库错误: {str(e)}'
        }

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

def get_all_users(page=1, per_page=10):
    """获取分页的用户列表
    Args:
        page: 页码(从1开始)
        per_page: 每页记录数
    Returns:
        tuple: (用户列表, 总数)
    """
    with DBSession() as session:
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 获取分页数据
        users = session.query(User).order_by(User.user_id)\
            .offset(offset).limit(per_page).all()
            
        # 获取总数
        total = session.query(User).count()
        
        return users, total

def update_user(user_id, update_data):
    """更新用户信息
    Args:
        user_id: 用户ID
        update_data: 更新数据 {username?, role?, password?}
    Returns:
        dict: 更新后的用户信息 {
            'user_id': 用户ID,
            'username': 用户名,
            'role': 用户角色
        }
    Raises:
        ValueError: 用户不存在或更新失败
    """
    with DBSession() as session:
        user = session.query(User).get(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        if 'username' in update_data:
            user.username = update_data['username']
        
        if 'role' in update_data:
            user.role = update_data['role']
        
        if 'password' in update_data:
            user.set_password(update_data['password'])
        
        session.commit()
        
        return {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role
        }
