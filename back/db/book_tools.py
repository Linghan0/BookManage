# -*- coding: utf-8 -*-

from back.db import get_session
from back.models import Book, UserBook

def get_all_books():
    """获取所有书籍"""
    session = get_session()
    try:
        books = session.query(Book).all()
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

def create_book(data):
    """创建新书"""
    session = get_session()
    try:
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
        return {'message': 'Book created'}
    finally:
        session.close()

def get_book_by_isbn(isbn):
    """根据ISBN获取书籍详情"""
    session = get_session()
    try:
        book = session.query(Book).filter_by(isbn=isbn).first()
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

def update_book(isbn, data):
    """更新书籍信息"""
    session = get_session()
    try:
        book = session.query(Book).filter_by(isbn=isbn).first()
        if not book:
            return None
            
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.publisher = data.get('publisher', book.publisher)
        session.commit()
        return {'message': 'Book updated'}
    finally:
        session.close()

def delete_book(isbn):
    """删除书籍"""
    session = get_session()
    try:
        book = session.query(Book).filter_by(isbn=isbn).first()
        if not book:
            return None
            
        session.delete(book)
        session.commit()
        return {'message': 'Book deleted'}
    finally:
        session.close()

def fetch_book_auto(isbn):
    """从国家图书馆API获取书籍信息"""
    from back.tools.bookdata import get_book_info, get_book_data
    
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
