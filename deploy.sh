#!/bin/bash

# 部署脚本
# 1. 构建前端
# 2. 启动后端服务
# 3. 配置Nginx

echo "=== 开始部署 ==="

# 检查依赖
echo "检查依赖..."
command -v npm >/dev/null 2>&1 || { echo >&2 "需要npm但未安装"; exit 1; }
command -v pip >/dev/null 2>&1 || { echo >&2 "需要pip但未安装"; exit 1; }
command -v uwsgi >/dev/null 2>&1 || { echo >&2 "需要uWSGI但未安装，请先执行: pip install uwsgi"; exit 1; }

# 前端构建
echo "构建前端..."
cd vite-test
npm install
if ! npm run build; then
    echo "前端构建失败!"
    exit 1
fi
cd ..

# 后端准备
echo "准备后端..."
cd back
pip install -r requirements.txt

# 检查数据库
echo "检查数据库..."
if [ ! -f "db/book_manage.db" ]; then
    echo "初始化数据库..."
    flask init-db
fi

# 启动后端服务 (使用生产环境配置)
echo "启动后端服务..."
export FLASK_ENV=production
uwsgi --ini uwsgi.ini &

echo "=== 部署完成 ==="
echo "前端构建文件在: vite-test/dist"
echo "后端运行在: http://localhost:5000"
echo "使用命令查看日志: tail -f uwsgi.log"
