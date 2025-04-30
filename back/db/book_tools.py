# -*- coding: utf-8 -*-
import re

from db import get_session
from models import Book, UserBook
from tools.bookdata import get_book_info, get_book_data

def format_isbn(isbn: str) -> str:
    """格式化ISBN：移除所有非数字字符并验证长度"""
    cleaned_isbn = re.sub(r'[^\d]', '', isbn)
    if len(cleaned_isbn) not in (10, 13):
        raise ValueError('ISBN必须是10位或13位数字')
    return cleaned_isbn


## 查询

# 从国家图书馆API获取书籍信息
def fetch_book_auto(isbn):
    """从国家图书馆API获取书籍信息"""

    
    try:
        # 获取原始书籍数据
        raw_data = get_book_info(isbn)
        if not raw_data or "error" in raw_data:
            return None
            
        # 转换为数据库格式
        book_data = get_book_data(raw_data)
        if not book_data:
            return None
            
        return book_data
    except Exception as e:
        import logging
        logging.error(f"获取书籍信息失败: {e}")
        return None

# 根据ISBN获取书籍
def get_book_by_isbn(isbn):
    """根据ISBN获取书籍详情"""
    session = get_session()
    try:
        formatted_isbn = format_isbn(isbn)
        book = session.query(Book).filter_by(isbn=formatted_isbn).first()
        if not book:
            return None
            
        return {
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'translator': book.translator or '',
            'genre': book.genre or '',
            'country': book.country or '',
            'era': book.era or '',
            'opac_nlc_class': book.opac_nlc_class or '',
            'publisher': book.publisher,
            'publish_year': book.publish_year,
            'page': book.page,
            'cover_url': book.cover_url or '',
            'description': book.description or ''
        }
    finally:
        session.close()

# 获取书籍总数
def get_books_count():
    """获取书籍总数"""
    session = get_session()
    try:
        return session.query(Book).count()
    finally:
        session.close()

# 获取所有书籍(支持分页)
def get_all_books(page=None, per_page=None):
    """获取所有书籍(支持分页)
    Args:
        page: 页码(从1开始)
        per_page: 每页数量
    Returns:
        list: 书籍列表，每条数据保持原有结构
    """
    session = get_session()
    try:
        query = session.query(Book)
        
        # 应用分页
        if page is not None and per_page is not None:
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
        books = query.all()
        return [{
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'translator': book.translator or '',
            'genre': book.genre or '',
            'country': book.country or '',
            'era': book.era or '',
            'opac_nlc_class': book.opac_nlc_class or '',
            'publisher': book.publisher,
            'publish_year': book.publish_year,
            'page': book.page,
            'cover_url': book.cover_url or '',
            'description': book.description or ''
        } for book in books]
    finally:
        session.close()

# 根据关键字搜索图书
def search_books(field, value):
    """根据字段搜索图书
    参数:
        field: 搜索字段(isbn/title/author)
        value: 搜索值
    返回:
        图书列表
    异常:
        ValueError: 搜索字段无效
        Exception: 搜索结果为空
    """
    session = get_session()
    try:
        valid_fields = ['isbn', 'title', 'author']
        if field not in valid_fields:
            raise ValueError('Invalid search field')
        
        if field == 'isbn':
            # 先查询本地数据库
            books = session.query(Book).filter(Book.isbn.like(f'%{value}%')).all()
            
            # 如果没有结果，尝试从API获取
            if not books:
                book_data = fetch_book_auto(value)
                if book_data:
                    # 创建书籍记录
                    create_book(book_data)
                    # 重新查询
                    books = session.query(Book).filter_by(isbn=value).all()
                    
        elif field == 'title':
            books = session.query(Book).filter(Book.title.like(f'%{value}%')).all()
        else:
            books = session.query(Book).filter(Book.author.like(f'%{value}%')).all()
        
        if not books:
            raise Exception('No books found matching the search criteria')
        
        return [book.to_dict() for book in books]
    finally:
        session.close()

# 获取用户书籍总数
def get_user_books_count(user_id):
    """获取用户书籍总数"""
    session = get_session()
    try:
        return session.query(UserBook).filter_by(user_id=user_id).count()
    finally:
        session.close()

# 获取用户书架中的书籍
def get_user_books(user_id, page=None, per_page=None):
    """获取用户书架中的书籍(支持分页)
    Args:
        user_id: 用户ID
        page: 页码(从1开始)
        per_page: 每页数量
    Returns:
        list: 用户书籍列表，每条数据保持原有结构
    """
    session = get_session()
    try:
        query = session.query(UserBook).filter_by(user_id=user_id)
        
        # 应用分页
        if page is not None and per_page is not None:
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
        user_books = query.all()
        return [{
            'isbn': ub.book.isbn,
            'title': ub.book.title,
            'author': ub.book.author,
            'nums': ub.nums
        } for ub in user_books]
    finally:
        session.close()




# 增加


# 创建书籍
def create_book(data):
    """创建新书"""
    session = get_session()
    try:
        # 必填字段验证
        required_fields = ['isbn', 'title']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"缺少必填字段: {field}")

        # 创建书籍记录
        book = Book(
            isbn=data['isbn'],
            title=data['title'],
            author=data.get('author', ''),
            translator=data.get('translator', ''),
            genre=data.get('genre', ''),
            country=data.get('country', ''),
            era=data.get('era', ''),
            opac_nlc_class=data.get('opac_nlc_class', ''),
            publisher=data.get('publisher', ''),
            publish_year=data.get('publish_year'),
            page=data.get('page'),
            cover_url=data.get('cover_url', ''),
            description=data.get('description', '')
        )
        session.add(book)
        session.commit()
        return {
            'success': True,
            'message': 'Book created',
            'book': {
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'publisher': book.publisher
            }
        }
    finally:
        session.close()

# 根据ISBN创建新书
def create_book_isbn(isbn):
    """根据ISBN创建新书
    Args:
        isbn: 书籍ISBN号
    Returns:
        dict: {
            'success': bool,  # 操作是否成功
            'message': str,   # 结果消息
            'book': dict      # 创建的书籍信息(成功时)
        }
    """
    session = get_session()
    try:
        # 检查书籍是否已存在
        existing_book = session.query(Book).filter_by(isbn=isbn).first()
        if existing_book:
            return {
                'success': False,
                'message': f'书籍已存在: {existing_book.title}',
                'book': None
            }

        # 从API获取书籍信息
        book_data = fetch_book_auto(isbn)
        if not book_data:
            return {
                'success': False,
                'message': '无法从API获取书籍信息',
                'book': None
            }

        # 使用create_book创建书籍
        result = create_book(book_data)
        if not result.get('success', False):
            return {
                'success': False,
                'message': result.get('message', '创建书籍失败'),
                'book': None
            }

        # 获取创建的书籍信息
        new_book = session.query(Book).filter_by(isbn=isbn).first()
        return {
            'success': True,
            'message': '书籍创建成功',
            'book': {
                'isbn': new_book.isbn,
                'title': new_book.title,
                'author': new_book.author,
                'publisher': new_book.publisher
            }
        }
    except Exception as e:
        session.rollback()
        import logging
        logging.error(f"创建书籍时发生错误: {str(e)}")
        return {
            'success': False,
            'message': f'创建书籍时发生错误: {str(e)}',
            'book': None
        }
    finally:
        session.close()


## 修改


# 更新书籍信息
def update_book(isbn, data):
    """更新书籍信息
    Args:
        isbn: 要更新的书籍ISBN
        data: 包含更新字段的字典
    Returns:
        dict: {
            'success': bool,  # 操作是否成功
            'message': str,    # 结果消息
            'book': dict       # 更新后的书籍信息(成功时)
        }
    Raises:
        ValueError: 如果ISBN无效或必填字段缺失
    """
    session = get_session()
    try:
        # 验证ISBN格式
        formatted_isbn = format_isbn(isbn)
        
        # 获取要更新的书籍
        book = session.query(Book).filter_by(isbn=formatted_isbn).first()
        if not book:
            return {
                'success': False,
                'message': '书籍不存在',
                'book': None
            }
            
        # 更新可修改字段
        updatable_fields = [
            'title', 'author', 'translator', 'genre', 'country', 
            'era', 'opac_nlc_class', 'publisher', 'publish_year',
            'page', 'cover_url', 'description'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(book, field, data[field])
        
        # 提交更改
        session.commit()
        
        # 返回更新后的书籍数据
        return {
            'success': True,
            'message': '书籍更新成功',
            'book': {
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'translator': book.translator,
                'genre': book.genre,
                'country': book.country,
                'era': book.era,
                'opac_nlc_class': book.opac_nlc_class,
                'publisher': book.publisher,
                'publish_year': book.publish_year,
                'page': book.page,
                'cover_url': book.cover_url,
                'description': book.description
            }
        }
    except ValueError as e:
        session.rollback()
        return {
            'success': False,
            'message': f'参数错误: {str(e)}',
            'book': None
        }
    except Exception as e:
        session.rollback()
        import logging
        logging.error(f"更新书籍失败: {str(e)}")
        return {
            'success': False,
            'message': f'更新书籍失败: {str(e)}',
            'book': None
        }
    finally:
        session.close()


## 删除


# 删除书籍
def delete_book(isbn):
    """删除书籍
    先删除用户书籍关联，再删除书籍本身
    使用事务确保数据一致性
    """
    session = get_session()
    try:
        # 开始事务并打印详细日志
        session.begin()
        print(f"Starting transaction to delete book with ISBN: {isbn}")
        
        # 1. 先删除用户书籍关联
        print("Deleting user-book associations...")
        deleted_count = session.query(UserBook).filter_by(isbn=isbn).delete()
        print(f"Deleted {deleted_count} user-book associations")
        
        # 2. 删除书籍本身
        print("Deleting book record...")
        book = session.query(Book).filter_by(isbn=isbn).first()
        if not book:
            session.rollback()
            print(f"Book with ISBN {isbn} not found - rolling back transaction")
            return {
                'success': False,
                'message': '书籍不存在'
            }
            
        session.delete(book)
        session.commit()
        print(f"Successfully committed deletion of book with ISBN {isbn}")
        
        # 验证删除是否成功
        book_exists = session.query(Book).filter_by(isbn=isbn).first()
        if book_exists:
            print("WARNING: Book still exists after deletion!")
        else:
            print("Book successfully deleted from database")
        
        return {
            'success': True,
            'message': '书籍删除成功'
        }
        
    except Exception as e:
        session.rollback()
        import logging
        logging.error(f"删除书籍失败: {str(e)}", exc_info=True)
        print(f"Error deleting book: {str(e)} - rolling back transaction")
        
        # 检查是否是外键约束错误
        if "foreign key constraint" in str(e).lower():
            return {
                'success': False,
                'message': '删除失败：存在关联数据'
            }
            
        return {
            'success': False,
            'message': f'删除书籍失败: {str(e)}'
        }
    finally:
        session.close()
        print("Database session closed")


# 用户书籍


# 增加书籍到用户书架
def add_book_to_user(isbn, user_id):
    """普通用户添加书籍到个人书库"""
    session = get_session()
    try:
        # 检查书籍是否存在
        book = session.query(Book).filter_by(isbn=isbn).first()
        if not book:
            # 从外部API获取书籍信息
            book_data = fetch_book_auto(isbn)
            if not book_data:
                raise ValueError("无法获取书籍信息")
            
            # 创建书籍
            create_book(book_data)
            book = session.query(Book).filter_by(isbn=isbn).first()

        # 添加用户-书籍关联
        user_book = session.query(UserBook).filter_by(
            user_id=user_id, isbn=isbn
        ).first()
        
        if user_book:
            user_book.nums += 1
        else:
            user_book = UserBook(user_id=user_id, isbn=isbn)
            session.add(user_book)
            
        session.commit()
        return {'message': 'Book added to user'}
    finally:
        session.close()

# 从用户书架中移除书籍
def remove_book_from_user(isbn, user_id):
    """从用户书架中移除书籍
    Args:
        isbn: 书籍ISBN
        user_id: 用户ID
    Returns:
        dict: 操作结果消息
    Raises:
        ValueError: 如果书籍不在用户书架中
    """
    session = get_session()
    try:
        user_book = session.query(UserBook).filter_by(
            user_id=user_id,
            isbn=isbn
        ).first()
        
        if not user_book:
            raise ValueError('书籍不在用户书架中')
            
        session.delete(user_book)
        session.commit()
        return {'message': 'Book removed from user'}
    finally:
        session.close()
