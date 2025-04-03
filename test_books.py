# -*- coding: utf-8 -*-
import json
import requests
from pathlib import Path
from back.tools.bookdata import get_book_data

# 读取data.json
data_path = Path('back/tools/bookdata/data.json')
with open(data_path, 'r', encoding='utf-8') as f:
    books_data = json.load(f)

# 测试API端点
BASE_URL = 'http://127.0.0.1:5000/api'

# 处理并添加书籍
for book in books_data:
    # 转换数据格式
    db_data = get_book_data(book)
    if not db_data:
        print(f"数据转换失败: {book.get('title')}")
        continue
    
    # 添加书籍
    response = requests.post(
        f"{BASE_URL}/books",
        json=db_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        print(f"添加成功: {db_data['title']}")
    else:
        print(f"添加失败: {response.text}")

# 验证书籍列表
response = requests.get(f"{BASE_URL}/books")
if response.status_code == 200:
    print("\n当前书籍列表:")
    for book in response.json():
        print(f"- {book['title']} (ISBN: {book['isbn']})")
else:
    print("获取书籍列表失败")
