# 图书管理系统部署指南

## 系统要求
- Linux服务器(推荐Ubuntu 20.04+)
- Node.js 16+ (前端)
- Python 3.8+ (后端)
- Nginx (Web服务器)
- SQLite (数据库)

## 部署步骤

### 1. 安装系统依赖
```bash
# Ubuntu示例
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip nginx sqlite3
```

### 2. 克隆代码
```bash
git clone https://your-repo-url/BookManage.git #???
cd BookManage
```

### 3. 后端准备
```bash
cd back
pip install -r requirements.txt
```

### 4. 前端构建
```bash
cd ../vite-test
npm install
npm run build
```

### 5. 配置环境变量
- 后端: 编辑`back/.env.production`
- 前端: 编辑`vite-test/.env.production`

### 6. 启动后端服务
```bash
cd ../back
export FLASK_ENV=production
flask run --host=0.0.0.0 --port=5000 &
```

### 7. 配置Nginx
1. 复制`nginx.conf`到`/etc/nginx/sites-available/bookmanage`
2. 创建符号链接：
```bash
sudo ln -s /etc/nginx/sites-available/bookmanage /etc/nginx/sites-enabled/
```
3. 测试并重启Nginx：
```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 注意事项
1. 生产环境务必修改以下敏感信息：
   - 后端`.env.production`中的`SECRET_KEY`和`ADMIN_PASSWORD`
   - 前端`.env.production`中的API地址

2. 建议使用PM2管理后端进程：
```bash
npm install -g pm2
pm2 start "flask run --host=0.0.0.0 --port=5000" --name "bookmanage-backend"
```

3. 如需HTTPS，请配置SSL证书并启用nginx.conf中的HTTPS配置。

## 访问系统
- 前端: http://your-server-ip
- 后端API: http://your-server-ip:5000/api
