# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import jwt 
from datetime import datetime, timedelta
from functools import wraps
import configparser
from pathlib import Path
from flask import Flask, jsonify, request, Response, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os


from config import DB_PATH, SECRET_KEY
from models import User, Book
from db.init_db import init_database
from db import book_tools
from db.book_tools import (
    get_all_books,
    create_book,
    get_book_by_isbn,
    get_books_count,
    update_book,
    delete_book,
    add_book_to_user, 
    get_user_books, 
    remove_book_from_user,
    get_user_books_count
)
from db import DBSession
from db.user_tools import authenticate_user, get_user_by_id, register_user, get_all_users, update_user


# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))


# 配置封面图片存储路径
IMG_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COVER_FOLDER = os.path.join(IMG_BASE_DIR, 'src', 'img', 'book_covers')
DEFAULT_COVER = os.path.join(IMG_BASE_DIR, 'src', 'img', 'default_cover.jpg')

os.makedirs(COVER_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['COVER_FOLDER'] = COVER_FOLDER
app.config['DEFAULT_COVER'] = DEFAULT_COVER



# 配置文件路径
config_path = Path(__file__).parent / "config.ini"

# 读取或创建配置文件
config = configparser.ConfigParser()
if config_path.exists():
    config.read(config_path)
else:
    config['INIT'] = {'initialized': 'False'}

# 检查是否需要初始化
if config.getboolean('INIT', 'initialized', fallback=False) == False:
    print("首次启动，正在初始化数据库...")
    if not init_database(str(DB_PATH)):
        print("数据库初始化失败!")
        exit(1)
    # 更新初始化状态
    config['INIT']['initialized'] = 'True'
    with open(config_path, 'w') as f:
        config.write(f)
    print("数据库初始化完成，已更新初始化状态")
else:
    print("非首次启动，跳过数据库初始化")

# 全局CORS配置
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin and origin.startswith('http://localhost'):
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response.status_code = 200
    return response



def token_required(f):
    """
    JWT认证装饰器
    返回更详细的错误信息帮助调试
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            print("未提供Authorization头")
            return jsonify({
                'error': {
                    'type': 'auth_error',
                    'message': '缺少Authorization头',
                    'code': 'missing_auth_header'
                }
            }), 401
        
        # 统一处理Bearer token
        if not auth_header.startswith('Bearer '):
            print("Token格式错误，缺少Bearer前缀")
            return jsonify({
                'error': {
                    'type': 'auth_error',
                    'message': 'Token格式不正确，应以Bearer开头',
                    'code': 'invalid_token_format'
                }
            }), 401
            
        token = auth_header[7:].strip()
        
        try:
            # 解码并验证token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # 检查token过期
            if 'exp' in data and datetime.utcnow() > datetime.fromtimestamp(data['exp']):
                print(f"Token已过期: {data}")
                return jsonify({
                    'error': {
                        'type': 'auth_error',
                        'message': 'Token已过期',
                        'code': 'token_expired'
                    }
                }), 401
            
            # 验证用户存在
            user_id = data.get('user_id')
            if not user_id:
                print("Token缺少user_id")
                return jsonify({
                    'error': {
                        'type': 'auth_error',
                        'message': '无效的Token',
                        'code': 'invalid_token'
                    }
                }), 401
                
            current_user = get_user_by_id(user_id)
            if not current_user:
                print(f"用户不存在: {user_id}")
                return jsonify({
                    'error': {
                        'type': 'auth_error',
                        'message': '用户不存在',
                        'code': 'user_not_found'
                    }
                }), 401
            
            print(f"Token验证成功 - 用户: {current_user.username} (ID: {current_user.user_id})")
            return f(current_user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError as e:
            print(f"Token过期: {str(e)}")
            return jsonify({
                'error': {
                    'type': 'auth_error',
                    'message': 'Token已过期',
                    'code': 'token_expired'
                }
            }), 401
        except jwt.InvalidTokenError as e:
            print(f"无效Token: {str(e)}")
            return jsonify({
                'error': {
                    'type': 'auth_error',
                    'message': '无效的Token',
                    'code': 'invalid_token'
                }
            }), 401
        except Exception as e:
            import traceback
            print(f"Token验证异常: {str(e)}")
            print(traceback.format_exc())
            
            # 统一错误响应格式
            error_data = {
                'error': {
                    'type': 'auth_error',
                    'code': 'token_validation_failed',
                    'message': 'Token验证失败'
                }
            }
            
            # 添加调试信息（仅开发环境）
            if app.debug:
                error_data['error']['details'] = str(e)
                error_data['error']['traceback'] = traceback.format_exc()
            
            return jsonify(error_data), 401
            
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

@app.route('/api/validate', methods=['GET'])
@token_required
def validate_token(current_user):
    """验证token有效性并返回用户信息"""
    return jsonify({
        'user_id': current_user.user_id,
        'username': current_user.username,
        'role': current_user.role
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

@app.route('/api/books/<isbn>', methods=['GET'])
def handle_book(isbn):
    try:
        book = get_book_by_isbn(isbn)
        if not book:
            return jsonify({
                'success': False,
                'message': '书籍不存在'
            }), 404
        return jsonify({
            'success': True,
            'book': book
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取书籍信息失败: {str(e)}'
        }), 500

@app.route('/api/books/<isbn>', methods=['PUT'])
@token_required
def update_book_route(current_user, isbn):
    """更新书籍信息(仅管理员)"""
    try:
        # 检查管理员权限
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': '权限不足: 只有管理员可以修改书籍'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '缺少请求数据'
            }), 400
            
        result = update_book(isbn, data)
        if not result['success']:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新书籍失败: {str(e)}'
        }), 500

@app.route('/api/books/<isbn>', methods=['DELETE'])
@token_required
def delete_book_route(current_user, isbn):
    """删除书籍(仅管理员)"""
    try:
        # 检查管理员权限
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': '权限不足: 只有管理员可以删除书籍'
            }), 403
            
        result = delete_book(isbn)
        if not result['success']:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除书籍失败: {str(e)}'
        }), 500

@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    """创建用户(仅管理员)
    成功返回:
        {
            "user_id": 用户ID,
            "username": 用户名,
            "role": 用户角色,
            "message": "用户创建成功"
        }
    错误返回:
        {
            "error": {
                "type": "validation_error|database_error|auth_error",
                "message": "详细错误信息",
                "field": "导致错误的字段名(可选)"
            }
        }
    """
    # 检查管理员权限
    if current_user.role != 'admin':
        return jsonify({
            'error': {
                'type': 'auth_error',
                'message': '权限不足: 只有管理员可以创建用户'
            }
        }), 403
    
    # 验证请求数据
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'error': {
                'type': 'validation_error',
                'message': '用户名和密码不能为空',
                'field': 'username' if not data.get('username') else 'password'
            }
        }), 400
    
    # 使用改进后的register_user函数创建用户
    result = register_user(
        username=data['username'],
        hashed_password=data['password'],
        role=data.get('role', 'user')
    )
    
    # 处理结果
    if isinstance(result, dict) and 'type' in result:  # 错误情况
        return jsonify({'error': result}), 400
    elif isinstance(result, User):  # 成功情况
        return jsonify({
            'user_id': result.user_id,
            'username': result.username,
            'role': result.role,
            'message': '用户创建成功'
        }), 201
    else:  # 未知错误
        return jsonify({
            'error': {
                'type': 'server_error',
                'message': '未知服务器错误'
            }
        }), 500

@app.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    """获取用户列表(仅管理员)
    参数:
        page: 页码(默认1)
        size: 每页数量(默认10)
    返回:
        {
            "users": [
                {
                    "user_id": 用户ID,
                    "username": 用户名,
                    "role": 用户角色
                },
                ...
            ],
            "total": 总数,
            "page": 当前页码,
            "per_page": 每页数量
        }
    """
    # 检查管理员权限
    if current_user.role != 'admin':
        return jsonify({
            'error': {
                'type': 'auth_error',
                'message': '权限不足: 只有管理员可以查看用户列表'
            }
        }), 403
    
    # 获取分页参数
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('size', 10))
    
    # 获取用户数据
    users, total = get_all_users(page=page, per_page=per_page)
    
    # 格式化响应
    return jsonify({
        'users': [{
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role
        } for user in users],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/users/check', methods=['GET'])
@token_required
def check_username(current_user):
    """检查用户名是否可用
    返回:
        {
            "available": true/false
        }
    """
    if current_user.role != 'admin':
        return jsonify({
            'error': {
                'type': 'auth_error',
                'message': '权限不足: 只有管理员可以检查用户名'
            }
        }), 403
    
    username = request.args.get('username')
    if not username:
        return jsonify({
            'error': {
                'type': 'validation_error',
                'message': '必须提供username参数',
                'field': 'username'
            }
        }), 400
    
    with DBSession() as session:
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'available': user is None})

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def manage_user(current_user, user_id):
    """管理用户(仅管理员)"""
    if current_user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    with DBSession() as session:
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        if request.method == 'GET':
            # 获取单个用户信息
            user = get_user_by_id(user_id)
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            return jsonify({
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role,
                'createdAt': user.created_at.isoformat() if user.created_at else None
            })
    
        if request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'message': '无效的请求数据'}), 400
            
            try:
                updated_user = update_user(user_id, data)
                return jsonify({
                    'message': '用户更新成功',
                    'user': updated_user
                })
            except ValueError as e:
                return jsonify({'message': str(e)}), 400
            
        elif request.method == 'DELETE':
            if user.role == 'admin':
                return jsonify({
                    'error': {
                        'type': 'auth_error',
                        'message': '不能删除管理员用户'
                    }
                }), 400
            session.delete(user)
            session.commit()
            return jsonify({'message': '用户删除成功'})

@app.route('/api/books/search', methods=['GET'])
def search_books():
    search_field = request.args.get('field')
    search_value = request.args.get('value')
    
    if not search_field or not search_value:
        return jsonify({'error': 'Missing search parameters'}), 400
    
    try:
        books = book_tools.search_books(search_field, search_value)
        return jsonify(books)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f'Search error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/bookshelf', methods=['GET'])
@token_required
def get_bookshelf(current_user):
    """获取用户书架"""
    # 获取用户所有书籍数据并转换为字典
    bookshelf = get_user_books(user_id=current_user.user_id)
    return jsonify(bookshelf), 201


@app.route('/api/bookshelf/<isbn>', methods=['POST', 'DELETE'])
@token_required
def manage_bookshelf(current_user, isbn):
    """管理用户书架"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            quantity = data.get('quantity', 1)
            result = add_book_to_user(isbn, current_user.user_id, quantity)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'添加书籍失败: {str(e)}'}), 500
            
    elif request.method == 'DELETE':
        with DBSession() as session:
            result = remove_book_from_user(isbn, current_user.user_id)
            if not result:
                return jsonify({'error': 'Book not found in your shelf'}), 404
            return jsonify(result)


# 封面图片上传API
@app.route('/api/img/cover/upload', methods=['POST'])
@token_required
def upload_image(current_user):
    """上传图片"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['COVER_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'url': f'/api/img/cover/{filename}'}), 201

# 图片访问API
@app.route('/api/img/cover/<filename>')
def get_image(filename):
    """获取图片"""
    try:
        # 构建文件路径
        filepath = os.path.join(app.config['COVER_FOLDER'], filename)

        # 检查文件是否存在
        if not os.path.exists(filepath):
            raise FileNotFoundError
        
        # 首先尝试返回请求的封面
        return send_from_directory(app.config['COVER_FOLDER'], filename)
    except FileNotFoundError:
        # 确保默认封面文件存在
        if os.path.exists(app.config['DEFAULT_COVER']):
            print(f"返回默认封面: {app.config['DEFAULT_COVER']}")
            return send_file(app.config['DEFAULT_COVER'], mimetype='image/jpeg')
        # 如果默认封面也不存在，返回404
        return jsonify({'error': 'Default cover not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
