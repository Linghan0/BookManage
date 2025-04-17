# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import jwt 
from datetime import datetime, timedelta
from functools import wraps

from models import User
# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import DB_PATH, SECRET_KEY
from db.init_db import init_database
from db.book_tools import (
    get_all_books,
    create_book,
    get_book_by_isbn,
    get_books_count,
    update_book,
    delete_book
)
from db.user_tools import authenticate_user, get_db_session, get_user_by_id

from db.book_tools import (
    add_book_to_user, 
    get_user_books, 
    remove_book_from_user,
    get_user_books_count
)


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# 初始化数据库
if not init_database(str(DB_PATH)):
    print("数据库初始化失败!")
    exit(1)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://localhost:8082"]}})  # 允许跨域

def token_required(f):
    """
    JWT认证装饰器
    工作原理：
    1. 从请求头获取Authorization token
    2. 使用SECRET_KEY验证token签名
    3. 解码token获取用户信息
    4. 检查用户是否存在
    5. token无效或过期会返回401错误
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # 解码JWT token，验证签名和过期时间
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # 根据token中的user_id获取用户
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录
    成功登录后返回JWT token，包含：
    - user_id: 用户唯一标识
    - exp: token过期时间(24小时后)
    - 使用HS256算法和SECRET_KEY签名
    """
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    user = authenticate_user(auth['username'], auth['password'])
    if not user:
        return jsonify({'message': '用户名或密码错误'}), 401
    
    # 生成JWT token，包含用户ID和24小时有效期
    token = jwt.encode({
        'user_id': user.user_id,  # 用户唯一标识
        'exp': datetime.utcnow() + timedelta(hours=24)  # 过期时间
    }, app.config['SECRET_KEY'], algorithm="HS256")  # 使用HS256算法和密钥签名
    
    return jsonify({
        'token': token,
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role
    })

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello, World!'})

@app.route('/api/books', methods=['GET', 'POST'])
def handle_books():
    if request.method == 'GET':
        # 获取分页参数，默认为第1页，每页20条
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 获取分页数据和总数
        books = get_all_books(page=page, per_page=per_page)
        total = get_books_count()
        
        return jsonify({
            'items': books,
            'total': total,
            'page': page,
            'per_page': per_page
        })
        
    elif request.method == 'POST':
        data = request.get_json()
        result = create_book(data)
        return jsonify(result), 201

@app.route('/api/books/<isbn>', methods=['GET', 'PUT', 'DELETE'])
def handle_book(isbn):
    if request.method == 'GET':
        book = get_book_by_isbn(isbn)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify(book)
        
    elif request.method == 'PUT':
        data = request.get_json()
        result = update_book(isbn, data)
        if not result:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify(result)
        
    elif request.method == 'DELETE':
        result = delete_book(isbn)
        if not result:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify(result)

@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    """创建用户(仅管理员)"""
    if current_user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    # 创建用户逻辑
    session = get_db_session()
    try:
        if session.query(User).filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400
            
        user = User(username=data['username'], role=data.get('role', 'user'))
        user.set_password(data['password'])
        session.add(user)
        session.commit()
        return jsonify({'message': '用户创建成功'}), 201
    finally:
        session.close()

@app.route('/api/users/<int:user_id>', methods=['PUT', 'DELETE'])
@token_required
def manage_user(current_user, user_id):
    """管理用户(仅管理员)"""
    if current_user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    session = get_db_session()
    try:
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        if request.method == 'PUT':
            data = request.get_json()
            if 'password' in data:
                user.set_password(data['password'])
            if 'role' in data:
                user.role = data['role']
            session.commit()
            return jsonify({'message': '用户更新成功'})
            
        elif request.method == 'DELETE':
            session.delete(user)
            session.commit()
            return jsonify({'message': '用户删除成功'})
    finally:
        session.close()



@app.route('/api/bookshelf', methods=['GET'])
@token_required
def get_user_books(current_user):
    """获取用户书架"""
    # 获取分页参数，默认为第1页，每页20条
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # 获取分页数据和总数
    books = get_user_books(current_user.user_id, page=page, per_page=per_page)
    total = get_user_books_count(current_user.user_id)
    
    return jsonify({
        'items': books,
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/bookshelf/<isbn>', methods=['POST', 'DELETE'])
@token_required
def manage_bookshelf(current_user, isbn):
    """管理用户书架"""
    if request.method == 'POST':
        try:
            result = add_book_to_user(isbn, current_user.user_id)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
            
    elif request.method == 'DELETE':
        session = get_db_session()
        try:
            result = remove_book_from_user(isbn, current_user.user_id)
            if not result:
                return jsonify({'error': 'Book not found in your shelf'}), 404
            return jsonify(result)
        finally:
            session.close()

if __name__ == '__main__':
    app.run(debug=True)
