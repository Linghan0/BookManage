# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import unittest
import bcrypt
from db.book_tools import (
    fetch_book_auto,
    get_book_by_isbn,
    create_book,
    update_book,
    delete_book
)
from db.user_tools import authenticate_user, get_user_by_username, delete_user, register_user

class TestBookTools(unittest.TestCase):
    def setUp(self):
        # 三本书籍的测试ISBN
        self.test_isbns = [
            "9787519430238",
            "978-7-5658-0227-0", 
            "978-7-5126-6693-1"
        ]
        # 确保测试书籍不存在
        for isbn in self.test_isbns:
            if get_book_by_isbn(isbn):
                delete_book(isbn)

    def tearDown(self):
        # 清理测试数据
        for isbn in self.test_isbns:
            if get_book_by_isbn(isbn):
                delete_book(isbn)

    def test_fetch_book_auto(self):
        """测试自动获取书籍信息"""
        for isbn in self.test_isbns:
            book_data = fetch_book_auto(isbn)
            self.assertIsNotNone(book_data)
            self.assertEqual(book_data['isbn'], isbn.replace("-", ""))

    def test_book_crud(self):
        """测试书籍CRUD操作"""
        test_isbn = self.test_isbns[0]  # 使用第一本书测试CRUD
        
        # 测试创建书籍
        test_book = {
            'isbn': test_isbn,
            'title': '测试书籍',
            'author': '测试作者',
            'publisher': '测试出版社'
        }
        create_result = create_book(test_book)
        self.assertEqual(create_result['message'], 'Book created')

        # 测试查询书籍
        book = get_book_by_isbn(test_isbn)
        self.assertEqual(book['title'], '测试书籍')

        # 测试更新书籍
        update_data = {'title': '更新后的标题'}
        update_result = update_book(test_isbn, update_data)
        self.assertEqual(update_result['message'], 'Book updated')
        updated_book = get_book_by_isbn(test_isbn)
        self.assertEqual(updated_book['title'], '更新后的标题')

        # 测试删除书籍
        delete_result = delete_book(test_isbn)
        self.assertEqual(delete_result['message'], 'Book deleted')
        self.assertIsNone(get_book_by_isbn(test_isbn))

class TestUserTools(unittest.TestCase):
    def setUp(self):
        # 测试用户信息
        self.username = "test"
        self.raw_password = "123456"
        # 模拟前端加密
        self.hashed_password = bcrypt.hashpw(
            self.raw_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
    def test_password_encryption(self):
        """测试密码加密方式"""
        # 获取测试用户
        user = get_user_by_username(self.username)
        self.assertIsNotNone(user)
        
        # 验证密码加密方式为bcrypt
        self.assertTrue(bcrypt.checkpw(
            self.raw_password.encode('utf-8'),
            user.password.encode('utf-8')
        ))

    def test_user_authentication(self):
        """测试用户认证"""
        # 测试用户认证
        user = authenticate_user(self.username, self.raw_password)
        self.assertIsNotNone(user)
        
        # 测试查询用户
        db_user = get_user_by_username(self.username)
        self.assertEqual(db_user.username, self.username)
        
    def test_user_registration(self):
        """测试用户注册"""
        # 测试新用户注册
        new_username = "test_new"
        try:
            # 确保测试用户不存在
            if get_user_by_username(new_username):
                delete_user(new_username)
                
            # 注册新用户
            user = register_user(new_username, self.hashed_password)
            self.assertEqual(user.username, new_username)
            
            # 验证用户已创建
            db_user = get_user_by_username(new_username)
            self.assertEqual(db_user.username, new_username)
            
            # 验证密码正确
            self.assertTrue(bcrypt.checkpw(
                self.raw_password.encode('utf-8'),
                db_user.password.encode('utf-8')
            ))
        finally:
            # 清理测试用户
            if get_user_by_username(new_username):
                delete_user(new_username)
                
    def test_duplicate_username(self):
        """测试重复用户名注册"""
        with self.assertRaises(ValueError):
            register_user(self.username, self.hashed_password)
            
    def test_invalid_password_format(self):
        """测试无效密码格式"""
        with self.assertRaises(ValueError):
            register_user("test_invalid", "plaintext_password")

if __name__ == '__main__':
    unittest.main()
