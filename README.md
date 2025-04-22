# BookManage - 图书管理系统

基于Flask+Vue的个人图书管理系统（毕业设计项目）

## 技术栈

- **后端**
  - Python Flask
  - SQLite/MySQL
  - JWT认证

- **前端**
  - Vue3
  - Element Plus
  - Vite构建工具

## 功能特性

### 用户系统
- 用户登录/注销
- JWT token认证
- 管理员/普通用户角色区分

### 图书管理
- 图书列表浏览与搜索
- 图书详情查看
- 图书添加/编辑/删除（管理员）

### 用户管理（管理员）
- 用户列表查看
- 用户添加/编辑/删除
- 用户权限管理

### 个人书架
- 个人收藏图书管理
- 书架图书添加/移除

## 项目结构

```
BookManage/
├── back/                  # 后端代码
│   ├── app.py             # Flask主应用
│   ├── config.py          # 配置文件
│   ├── models.py          # 数据模型
│   ├── db/                # 数据库相关
│   │   ├── init_db.py     # 数据库初始化
│   │   ├── book_tools.py  # 图书操作工具
│   │   └── user_tools.py  # 用户操作工具
│   └── tools/             # 辅助工具
│
└── vite-test/             # 前端代码
    ├── src/
    │   ├── views/         # 页面组件
    │   ├── router/        # 路由配置
    │   ├── stores/        # 状态管理
    │   └── components/    # 公共组件
    └── vite.config.ts     # Vite配置
```

## 快速开始

### 前置要求
- Python 3.8+
- Node.js 16+
- SQLite/MySQL

### 后端启动
```bash
cd back
pip install -r requirements.txt

# 开发模式
flask run

# 生产模式
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 前端启动
```bash
cd vite-test
npm install
npm run dev
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
- [ ] 图书搜索功能
- [ ] 前端UI优化
- [ ] 图书分类管理
- [ ] 图书借阅/归还管理

## 许可证

MIT License
