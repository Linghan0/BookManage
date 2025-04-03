import sqlite3
import sys
from pathlib import Path
import bcrypt 
# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from back.config import DB_PATH, ADMIN_USERNAME, ADMIN_PASSWORD

def init_database(db_path=None):
    """初始化数据库"""
    # 如果没有传入路径，使用配置中的默认路径
    if db_path is None:
        db_path = str(DB_PATH)
    """
    Initialize SQLite database with required tables
    初始化SQLite数据库并创建所需表
    
    Parameters/参数:
        db_path: str - Path to the database file/数据库文件路径
    """
    try:
        db_path_obj = Path(db_path)
        
        # 检查数据库文件是否已存在
        db_exists = db_path_obj.exists()
        
        print("正在创建数据库目录...")
        # Create database directory if not exists/如果目录不存在则创建
        db_dir = db_path_obj.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"数据库目录已创建: {db_dir}")

        # 如果数据库已存在，只需验证连接
        if db_exists:
            print("数据库已存在，验证连接(Flask debug模式可能会显示多次)...")
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.close()
            print("数据库验证成功(实际只执行一次)")
            return True
        
        print("正在连接数据库...")
        # Connect to SQLite database with UTF-8 encoding/使用UTF-8编码连接SQLite数据库
        # SQLite will create the file if it doesn't exist/如果文件不存在会自动创建
        conn = sqlite3.connect(db_path)
        # 显式设置编码为UTF-8
        conn.execute("PRAGMA encoding = 'UTF-8'")
        # 确保文本处理正确处理Unicode
        conn.text_factory = str
        cursor = conn.cursor()
        print(f"数据库连接成功，编码设置为: {conn.execute('PRAGMA encoding').fetchone()[0]}")

        # SQLite与MySQL约束差异说明/Differences between SQLite and MySQL:
        # 1. SQLite使用动态类型，MySQL有严格类型/SQLite uses dynamic typing, MySQL has strict types
        # 2. SQLite长度约束仅CHECK实现，MySQL有原生长度限制/SQLite length limits via CHECK only
        # 3. 外键在SQLite中需要显式启用/Foreign keys need explicit enabling in SQLite
        
        # 数据库设置说明/Database settings:
        # 1. 编码设置为UTF-8/Encoding set to UTF-8
        # 2. 外键约束启用/Foreign keys enabled
        # 3. 文本处理使用Unicode/Text handling using Unicode
        
        cursor.execute("PRAGMA foreign_keys = ON")  # 启用外键约束/Enable foreign keys
        cursor.execute("PRAGMA encoding = 'UTF-8'")  # 确保UTF-8编码/Ensure UTF-8 encoding

        # Create User table/创建用户表
        # PRIMARY KEY: Unique identifier for each user/主键，唯一标识每个用户
        # AUTOINCREMENT: Automatically increment ID/自动递增ID
        # NOT NULL: Field cannot be empty/字段不能为空
        # UNIQUE: Username must be unique/用户名必须唯一
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 用户ID，主键
            username TEXT NOT NULL UNIQUE              -- 用户名，不能为空且唯一
                CHECK(length(username) BETWEEN 4 AND 20),  -- 用户名长度4-20字符
            password TEXT NOT NULL                     -- 密码，存储加密后的值
                CHECK(length(password) = 60),          -- bcrypt哈希固定60字符
            role TEXT NOT NULL DEFAULT 'user'          -- 角色，默认为user
                CHECK(role IN ('admin', 'user'))       -- 角色只能是admin或user
        )
        ''')

        # 创建默认管理员账户
        admin_username = ADMIN_USERNAME
        admin_password = ADMIN_PASSWORD  # 默认密码，首次登录后应修改
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 检查是否已存在管理员账户
        cursor.execute("SELECT COUNT(*) FROM User WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            cursor.execute('''
            INSERT INTO User (username, password, role)
            VALUES (?, ?, ?)
            ''', (admin_username, password_hash, 'admin'))
            print("已创建默认管理员账户")

        # Create Book table/创建书籍表
        # TEXT: String type/字符串类型
        # INTEGER: Integer type/整数类型
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Book (
            isbn TEXT PRIMARY KEY                     -- ISBN号，主键
                CHECK(length(isbn) BETWEEN 10 AND 13),  -- ISBN标准长度10或13位
            title TEXT NOT NULL                       -- 书名，不能为空
                CHECK(length(title) <= 100),          -- 书名最大100字符
            author TEXT                               -- 作者
                CHECK(length(author) <= 255),         -- 作者名最大255字符
            translator TEXT                           -- 译者
                CHECK(length(translator) <= 255),      -- 译者名最大255字符
            genre TEXT                                -- 小说类型
                CHECK(length(genre) <= 30),           -- 类型最大30字符
            country TEXT                              -- 国家
                CHECK(length(country) <= 30),         -- 国家名最大30字符
            era TEXT                                  -- 时代
                CHECK(length(era) <= 20),             -- 时代描述最大20字符
            opac_nlc_class TEXT                       -- 中国国家图书馆分类号
                CHECK(length(opac_nlc_class) <= 20), -- 分类号最大20字符
            publisher TEXT                            -- 出版社
                CHECK(length(publisher) <= 100),      -- 出版社名最大100字符
            publish_year INTEGER                      -- 出版年
                CHECK(publish_year BETWEEN 1800 AND 2100),  -- 出版年范围限制
            page INTEGER                        -- 页数
                CHECK(page > 0),                -- 页数必须为正数
            cover_url TEXT                            -- 封面图片URL
                CHECK(length(cover_url) <= 255),      -- URL最大255字符
            description TEXT                          -- 简介
                CHECK(length(description) <= 1000)    -- 简介最大1000字符
        )
        ''')

        # Create UserBook association table/创建用户书籍关联表
        # FOREIGN KEY: References primary key in another table/外键，引用其他表的主键
        # DEFAULT: Default value when not specified/未指定时的默认值
        # PRIMARY KEY (composite): Combination of user_id and book_isbn is unique
        # 复合主键：user_id和book_isbn的组合必须唯一
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserBook (
            user_id INTEGER,                           -- 用户ID，外键
            isbn TEXT,                                 -- 书籍ISBN，外键
            nums INTEGER DEFAULT 1                     -- 数量，默认为1
                CHECK(nums > 0),                       -- 数量必须为正数
            PRIMARY KEY (user_id, isbn),               -- 复合主键
            FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,  -- 级联删除
            FOREIGN KEY (isbn) REFERENCES Book(isbn) ON DELETE CASCADE         -- 级联删除
        )
        ''')

        conn.commit()
        print(f"Database initialized successfully at {db_path}")
        print(f"数据库已成功初始化，路径: {db_path}")
        return True

    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        print(f"Database initialization failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if not init_database():
        print("数据库初始化失败，请检查错误信息")
        print("Database initialization failed, please check error messages")
        exit(1)
