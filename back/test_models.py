# -*- coding: utf-8 -*-
# back/test_models.py

import json
from werkzeug.security import generate_password_hash
from pathlib import Path
from .db import init_db, DBSession
from .models import User, Book, UserBook
from .tools.bookdata import get_book_data

def test_models():
    """测试模型功能"""
    print("初始化数据库...")
    engine = init_db()
    
    print("\n测试用户模型...")
    with DBSession() as session:
        # 清理可能存在的测试用户
        session.query(User).filter_by(username="testuser").delete()
        
        # 创建测试用户(密码哈希)
        hashed_pw = generate_password_hash("testpass")
        user = User(username="testuser", password=hashed_pw)
        session.add(user)
        session.commit()
        print(f"创建用户: {user.username} (ID: {user.user_id})")
        
        # 从data.json加载测试图书数据
        project_root = Path(__file__).resolve().parent.parent
        data_path = project_root / "back" / "tools" / "bookdata" / "data.json"
        print(f"尝试从路径加载数据: {data_path}")
        if not data_path.exists():
            # 尝试另一种路径结构
            alt_path = project_root / "tools" / "bookdata" / "data.json"
            print(f"尝试备用路径: {alt_path}")
            if alt_path.exists():
                data_path = alt_path
            else:
                raise FileNotFoundError(f"无法找到数据文件，尝试路径:\n1. {data_path}\n2. {alt_path}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            test_books = json.load(f)
        print(f"成功加载 {len(test_books)} 条图书数据")
        
        # 处理并添加图书数据
        for book_data in test_books:
            formatted_data = get_book_data(book_data)
            if not formatted_data:
                print(f"跳过无效图书数据: {book_data.get('title', '未知')}")
                continue
                
            book = Book(
                isbn=formatted_data['isbn'],
                title=formatted_data['title'],
                author=formatted_data['author'][0] if formatted_data['author'] else "",
                translator=formatted_data['translator'],
                genre=formatted_data['genre'],
                country=formatted_data['country'],
                era=formatted_data['era'],
                opac_nlc_class=formatted_data['opac_nlc_class'],
                publisher=formatted_data['publisher'],
                publish_year=int(formatted_data['publish_year']) if formatted_data['publish_year'] else 0,
                page=formatted_data['page'],
                description=formatted_data['description']
            )
            session.add(book)
            
            # 创建关联关系
            user_book = UserBook(user_id=user.user_id, isbn=book.isbn)
            session.add(user_book)
            
        session.commit()
        print(f"成功添加 {len(test_books)} 本图书")
        
        # 查询测试
        print("\n查询测试结果:")
        queried_user = session.query(User).filter_by(username="testuser").first()
        print(f"查询用户: {queried_user.username}")
        
        books = session.query(Book).all()
        print(f"查询到 {len(books)} 本图书:")
        for book in books:
            print(f"- {book.title} (ISBN: {book.isbn})")
        
        print("测试完成")

if __name__ == "__main__":
    test_models()
