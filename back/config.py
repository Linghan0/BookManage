# -*- coding: utf-8 -*-
# back/config.py

from pathlib import Path

# 项目根目录(back文件夹的父目录)
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DB_DIR = BASE_DIR / 'back' / 'db'
DB_PATH = DB_DIR / 'book_manage.db'

# 确保数据库目录存在
DB_DIR.mkdir(parents=True, exist_ok=True)

# 安全配置
SECRET_KEY = 'django-insecure-!@#$%^&amp;*()_+abcdefghijklmnopqrstuvwxyz1234567890'

# 管理员账号密码
ADMIN_USERNAME = 'LingHan'
ADMIN_PASSWORD = 'askljdhgliuc'
