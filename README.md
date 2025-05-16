# BookManage - 图书管理系统

基于Flask+Vue的个人图书管理系统（毕业设计项目）

## 项目背景
- 为个人图书收藏管理提供数字化解决方案
- 实现图书信息的电子化管理和可视化展示
- 毕业设计项目，展示全栈开发能力

## 技术栈

### 后端
- Python 3.10+
- Flask 2.3.2
- SQLAlchemy 2.0
- JWT认证
- Gunicorn/UWSGI(生产环境)

### 前端
- Vue 3.3
- Vite 4.3
- Element Plus 2.3
- Pinia 2.1
- Axios 1.4

## 系统架构
![系统架构图](docs/architecture.png)

采用前后端分离架构：
- 前端: Vue3 + Vite构建
- 后端: Flask RESTful API
- 数据库: SQLite/MySQL

## 功能特性

### 核心功能
- 用户认证(JWT)
- 图书CRUD管理
- 个人书架管理
- 图书搜索与筛选

### 管理员功能
- 用户管理
- 系统配置
- 数据统计

## 项目结构


```
back/
├── app.py              # Flask主应用
├── models.py           # 数据模型
├── db/                 # 数据库操作
│   ├── init_db.py      # 数据库初始化
│   ├── book_tools.py   # 图书操作
│   └── user_tools.py   # 用户操作
└── tools/              # 辅助工具

vite_front/
├── src/
│   ├── views/          # 页面组件
│   │   ├── HomeView.vue       # 首页
│   │   ├── LoginView.vue      # 登录页
│   │   ├── BooksView.vue      # 图书列表页
│   │   ├── BookDetailView.vue # 图书详情页
│   │   ├── UserBooksView.vue  # 个人书架页
│   │   ├── ScanBookView.vue   # 扫码添加页
│   │   └── admin/             # 管理后台页面
│   │       ├── BooksView.vue      # 图书管理
│   │       ├── UsersView.vue      # 用户管理
│   │       ├── EditUserView.vue   # 用户编辑
│   │       └── RegisterView.vue   # 用户注册
│   ├── App.vue           # 入口组件
│   ├── router/         # 路由配置
│   ├── stores/         # 状态管理(Pinia)
│   │   ├── books.ts    # 图书状态管理
│   │   ├── user.ts     # 用户状态管理
│   │   └── shelfCache.ts # 书架缓存管理
│   ├── components/     # 公共组件
│   │   ├── HelloWorld.vue # 示例组件
│   │   └── NavBar.vue    # 导航栏组件
│   ├── utils/          # 工具函数
│   │   ├── http.ts     # HTTP请求封装
│   │   └── indexedDB.ts # 本地存储工具
│   ├── assets/         # 静态资源
│   └── styles/         # 全局样式
└── vite.config.ts      # Vite配置
```

## 快速开始

### 开发环境
```bash
# 后端
cd back
pip install -r requirements.txt
flask run

# 前端 
cd vite-test
npm install
npm run dev
```

### 生产部署
```bash
# 使用Gunicorn部署后端 （我用的宝塔，py项目基本自动）
gunicorn -c gunicorn_conf.py app:app

# 构建前端
cd vite_front
npm run build
```

## 配置说明

### 后端配置
- 开发环境: `.env`文件
```ini
DATABASE_URL=sqlite:///data.db
SECRET_KEY=your-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

- 生产环境: `.env.production`文件,以模板为准
```ini
## 当前数据库配置无效，写死为www/wwwroot/BookManage/db/bookmanage.db
DATABASE_URL=mysql://user:password@localhost/bookmanage
SECRET_KEY=production-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
```

### 前端配置
`.env.production`配置项:
```ini
VITE_API_BASE_URL=http://your-api-domain.com
```

## API文档

### 认证
- `POST /api/login` - 用户登录，获取JWT token

### 图书相关
- `GET /api/books` - 获取图书列表
- `POST /api/books` - 添加新图书（管理员）
- `GET/PUT/DELETE /api/books/<isbn>` - 图书详情/更新/删除

### 用户相关
- `POST /api/users` - 创建用户（管理员）
- `PUT/DELETE /api/users/<user_id>` - 更新/删除用户（管理员）

### 个人书架
- `GET /api/bookshelf` - 获取用户书架
- `POST/DELETE /api/bookshelf/<isbn>` - 添加/移除书架图书

## 待办事项
- [ ] 图书图片上传
- [√] 图书搜索功能
- [√] 前端UI优化
- [ ] 图书分类管理
- [ ] 图书借阅/归还管理

## 界面预览
![登录界面](docs/login.png)
![图书列表](docs/books.png)
![个人书架](docs/bookshelf.png)

## 许可证
MIT License
