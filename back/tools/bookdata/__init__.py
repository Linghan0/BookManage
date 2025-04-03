# -*- coding: utf-8 -*-
# __init__.py 标识为一个包

import json
import re
from .nlc_isbn import get_book_info, validate_isbn


def get_book_data(book_data):
    """
    将原始图书数据转换为简便格式
    :param book_data: 原始图书数据字典
    :return: 符合数据库结构的字典
    """
    if not book_data or "error" in book_data:
        return None
    # 提取ISBN
    isbn = book_data.get("isbn", "")
    # 提取书名
    title = (book_data.get("title", "") or "").split(" / ")[0] if book_data.get("title") else ""
    # 提取作者并转换为字符串(多位作者用；分隔，保留完整信息)
    authors = book_data.get("authors", []) or []
    author_str = "；".join(authors) if authors else ""
    
    # 提取译者
    translator = ""
    if " / " in book_data.get("title", ""):
        try:
            translator = book_data.get("title", "").split(";")[-1].split("译")[0].strip()
        except (IndexError, AttributeError):
            translator = ""
    # 提取出版年
    publish_year = book_data.get("pubdate", "") or ""
    # 提取封面URL
    cover_url = ""
    # 提取出版社
    publisher = book_data.get("publisher", "") or ""
    # 提取分类
    genre = book_data.get("tags", [])[0] if len(book_data.get("tags", [])) > 0 else ""
    # 提取国家
    country = book_data.get("tags", [])[1] if len(book_data.get("tags", [])) > 1 else ""
    # 提取时代
    era = book_data.get("tags", [])[2] if len(book_data.get("tags", [])) > 2 else ""
    # 提取中图分类
    opac_nlc_class = ""
    if len(book_data.get("tags", [])) > 3:
        try:
            opac_nlc_class = book_data.get("tags", [])[3].split(":")[-1].strip()
        except (IndexError, AttributeError):
            opac_nlc_class = ""
    # 提取页数 "pages": "208页 ; 23cm" 208
    page = 0
    if book_data.get("pages"):
        try:
            page = int(book_data.get("pages", "").split("页")[0])
        except (ValueError, IndexError, AttributeError):
            page = 0
    # 提取简介
    description = book_data.get("comment", "") or ""

    # 构建格式化数据
    db_data = {
        "isbn": isbn,
        "title": title[:100],
        "author": author_str[:255],
        "translator": translator[:255],
        "genre": genre[:30],
        "country": country[:30],
        "era": era[:20],
        "opac_nlc_class": opac_nlc_class[:20],
        "publisher": publisher[:100],
        "publish_year": publish_year,
        "page": page,
        "cover_url":cover_url[:255],
        "description": description[:1000],
    }
    
    # 验证必填字段
    if not db_data["isbn"] or not db_data["title"]:
        return None
    
    return db_data

if __name__ == '__main__':
    # 测试用例
    isbn = "978-7-5658-0227-0"
    #isbn = "978-7-5126-6693-1"
    book_info = get_book_info(isbn)
    print("原始数据:")
    print(json.dumps(book_info, ensure_ascii=False, indent=2))
    
    if book_info and "error" not in book_info:
        book_data = get_book_data(book_info)
        print("\n数据库格式:")
        print(json.dumps(book_data, ensure_ascii=False, indent=2))