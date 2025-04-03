# -*- coding: utf-8 -*-
# 测试数据导入脚本

import json
import os
from back.db.book_tools import create_book
from . import get_book_data

def import_test_data():
    # 获取测试数据文件路径
    data_file = os.path.join(os.path.dirname(__file__), 'data.json')
    
    # 读取测试数据
    with open(data_file, 'r', encoding='utf-8') as f:
        books_data = json.load(f)
    
    # 导入每本书
    for book_data in books_data:
        # 转换数据格式
        db_data = get_book_data(book_data)
        if not db_data:
            print(f"数据转换失败: {book_data.get('title')}")
            continue
        
        # 创建书籍
        result = create_book(db_data)
        print(f"导入书籍: {db_data['title']}, 结果: {result}")

if __name__ == "__main__":
    import_test_data()
