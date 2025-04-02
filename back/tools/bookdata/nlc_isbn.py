# -*- coding: utf-8 -*-
# nlc_isbn.py

import re
import urllib.request
import logging
from bs4 import BeautifulSoup

from headers import get_opacnlc_headers


BASE_URL = "http://opac.nlc.cn/F"
SEARCH_URL_TEMPLATE = BASE_URL + "?func=find-b&find_code=ISB&request={isbn}&local_base=NLC01" + \
                      "&filter_code_1=WLN&filter_request_1=&filter_code_2=WYR&filter_request_2=" + \
                      ("&filter_code_3=WYR&filter_request_3=&filter_code_4=WFM&filter_request_4=&filter_code_5=WSL"
                       "&filter_request_5=")


def get_dynamic_url(update_status):
    try:
        response = urllib.request.urlopen(urllib.request.Request(BASE_URL, headers=get_opacnlc_headers()), timeout=10)
        response_text = response.read().decode('utf-8')
        dynamic_url_match = re.search(r"http://opac.nlc.cn:80/F/[^\s?]*", response_text)
        if dynamic_url_match:
            update_status(f"动态URL: {dynamic_url_match.group(0)}")
            return dynamic_url_match.group(0)
        else:
            raise ValueError("无法找到动态URL")
    except Exception as e:
        update_status(f"获取动态URL时出错: {e}")
        return None


def isbn2meta(isbn, update_status):
    if not isinstance(isbn, str):
        update_status("ISBN必须是字符串")
        return None
    
    # 标准化ISBN，去除连字符等非数字字符
    clean_isbn = canonical(isbn)
    update_status(f"标准化后的ISBN: {clean_isbn}")
    
    try:
        isbn_match = re.match(r"\d{10,}", clean_isbn).group()
    except AttributeError:
        update_status(f"无效的ISBN代码: {isbn} (标准化后: {clean_isbn})")
        return None

    if isbn_match != clean_isbn:
        update_status(f"无效的ISBN代码: {isbn} (标准化后: {clean_isbn})")
        return None

    dynamic_url = get_dynamic_url(update_status)
    if not dynamic_url:
        return None

    search_url = SEARCH_URL_TEMPLATE.format(isbn=clean_isbn)
    update_status(f"构造的搜索URL: {search_url}")
    try:
        response = urllib.request.urlopen(urllib.request.Request(search_url, headers=get_opacnlc_headers()), timeout=10)
        response_text = response.read().decode('utf-8')
        soup = BeautifulSoup(response_text, "html.parser")
        return parse_metadata(soup, isbn, update_status)
    except Exception as e:
        update_status(f"获取元数据时出错: {e}")
        return None


def clean_string(text):
    """清理字符串中的特殊字符和多余空格"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)  # 替换多个空格为单个空格
    text = text.replace('\xa0', ' ').strip()
    return text

def parse_metadata(soup, isbn, update_status):
    data = {}
    prev_td1 = ''
    prev_td2 = ''

    try:
        table = soup.find("table", attrs={"id": "td"})
        if not table:
            update_status("未找到数据表格")
            return None

        tr_elements = table.find_all('tr')
        for tr in tr_elements:
            td_elements = tr.find_all('td', class_='td1')
            if len(td_elements) == 2:
                td1 = clean_string(td_elements[0].get_text())
                td2 = clean_string(td_elements[1].get_text())
                if not td1 and not td2:
                    continue
                if td1:
                    data[td1] = td2
                else:
                    data[prev_td1] = '\n'.join([prev_td2, td2])
                prev_td1 = td1
                prev_td2 = td2

        # 处理出版信息
        pub_info = data.get("出版项", "")
        pubdate = ""
        publisher = ""
        if pub_info:
            pubdate_match = re.search(r',\s*(\d{4})', pub_info)
            pubdate = pubdate_match.group(1) if pubdate_match else ""
            publisher_match = re.search(r':\s*(.+?)\s*,', pub_info)
            publisher = publisher_match.group(1) if publisher_match else ""

        # 处理标签
        tags = []
        subject = data.get("主题", "")
        if subject:
            tags.extend([clean_string(tag) for tag in re.split(r'[-—–&]+', subject) if clean_string(tag)])
        class_num = data.get("中图分类号", "")
        if class_num:
            tags.append(f"中图分类:{clean_string(class_num)}")
        if publisher:
            tags.append(f"出版社:{publisher}")
        if pubdate:
            tags.append(f"出版年:{pubdate}")

        # 处理作者
        authors = []
        author_text = data.get("著者", "")
        if author_text:
            authors = [clean_string(author) for author in re.split(r'[;&]', author_text) if clean_string(author)]

        metadata = {
            "title": clean_string(data.get("题名与责任", isbn)),
            "tags": [tag for tag in tags if tag],
            "comments": clean_string(data.get("内容提要", "")),
            "publisher": publisher,
            "pubdate": pubdate,
            "authors": authors,
            "isbn": isbn,
            "pages": clean_string(data.get("载体形态项", "")),
        }
        return metadata
    except Exception as e:
        update_status(f"解析元数据时出错: {e}")
        return None




# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ISBN处理函数
def canonical(isbnlike):
    """标准化ISBN，保留数字和X"""
    numb = [c for c in isbnlike if c in '0123456789Xx']
    if numb and numb[-1] == 'x':
        numb[-1] = 'X'
    isbn = ''.join(numb)
    if not isbn or len(isbn) not in (10, 13):
        return ''
    return isbn

def is_isbn10(isbn10):
    """验证ISBN-10格式"""
    isbn10 = canonical(isbn10)
    if len(isbn10) != 10:
        return False
    total = sum((i + 1) * int(x) for i, x in enumerate(isbn10[:-1]))
    check = 11 - (total % 11)
    if check == 10:
        check_char = 'X'
    elif check == 11:
        check_char = '0'
    else:
        check_char = str(check)
    return isbn10[-1].upper() == check_char

def is_isbn13(isbn13):
    """验证ISBN-13格式"""
    isbn13 = canonical(isbn13)
    if len(isbn13) != 13:
        return False
    if isbn13[0:3] not in ('978', '979'):
        return False
    total = sum((i % 2 * 2 + 1) * int(x) for i, x in enumerate(isbn13[:-1]))
    check = 10 - (total % 10)
    if check == 10:
        check = 0
    return int(isbn13[-1]) == check

def validate_isbn(isbn):
    """验证并规范化ISBN号码"""
    clean_isbn = canonical(isbn)
    if not clean_isbn:
        return None
    if len(clean_isbn) == 10 and is_isbn10(clean_isbn):
        return clean_isbn
    if len(clean_isbn) == 13 and is_isbn13(clean_isbn):
        return clean_isbn
    return None

def get_book_info(isbn):
    """
    通过ISBN获取书籍信息并返回JSON格式数据
    :param isbn: ISBN号码
    :return: 包含书籍信息的字典，可直接转为JSON
    """
    def update_status(message):
        logger.info(message)
    
    book_data = isbn2meta(isbn, update_status)
    return book_data if book_data else {"error": "Book not found"}

## 测试
if __name__ == "__main__":
    import json
    isbn = "9787519430238"
#    isbn = "978-7-5126-6693-1"
    book_info = get_book_info(isbn)
    print(json.dumps(book_info, ensure_ascii=False, indent=2))