# -*- coding: utf-8 -*-
# back/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import hashlib

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = 'User'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(64), nullable=False)  # 存储sha256加密后的密码
    role = Column(String(10), nullable=False, default='user')  # 'admin' or 'user'
    
    # 与Book的关系 (多对多)
    books = relationship("UserBook", back_populates="user")
    
    __table_args__ = (
        CheckConstraint('length(username) BETWEEN 4 AND 20', name='check_username_length'),
        CheckConstraint('length(password) = 64', name='check_password_length'),  # sha256哈希固定64字符
        CheckConstraint("role IN ('admin', 'user')", name='check_role_values'),
    )

    def set_password(self, hashed_password):
        """设置密码，接受前端sha256哈希值"""
        if len(hashed_password) != 64:
            raise ValueError("密码必须是64字符的sha256哈希值")
        self.password = hashed_password

    def check_password(self, hashed_password):
        """验证密码，直接比较sha256哈希值"""
        return self.password == hashed_password

    @staticmethod
    def ensure_single_admin(session):
        """确保只有一个管理员账户"""
        admins = session.query(User).filter_by(role='admin').all()
        if len(admins) > 1:
            # 保留第一个创建的管理员账户
            first_admin = min(admins, key=lambda u: u.user_id)
            for admin in admins:
                if admin.user_id != first_admin.user_id:
                    admin.role = 'user'
            session.commit()
            raise ValueError("检测到多个管理员账户，已自动将多余账户降级为普通用户")

class Book(Base):
    """图书模型"""
    __tablename__ = 'Book'
    
    isbn = Column(String(13), primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(255))
    translator = Column(String(255))
    genre = Column(String(30))
    country = Column(String(30))
    era = Column(String(20))
    opac_nlc_class = Column(String(20))
    publisher = Column(String(100))
    publish_year = Column(Integer)
    page = Column(Integer)
    cover_url = Column(String(255))
    description = Column(String(1000))
    
    # 与User的关系 (多对多)
    users = relationship("UserBook", back_populates="book")

    def to_dict(self):
        """将模型转换为字典"""
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'translator': self.translator,
            'genre': self.genre,
            'country': self.country,
            'era': self.era,
            'opac_nlc_class': self.opac_nlc_class,
            'publish_year': self.publish_year,
            'page': self.page,
            'cover_url': self.cover_url,
            'description': self.description
        }
    
    __table_args__ = (
        CheckConstraint('length(isbn) BETWEEN 10 AND 13', name='check_isbn_length'),
        CheckConstraint('publish_year BETWEEN 1800 AND 2100', name='check_publish_year'),
        CheckConstraint('page > 0', name='check_page_positive'),
    )

class UserBook(Base):
    """用户-图书关联模型"""
    __tablename__ = 'UserBook'
    
    user_id = Column(Integer, ForeignKey('User.user_id', ondelete="CASCADE"), primary_key=True)
    isbn = Column(String(13), ForeignKey('Book.isbn', ondelete="CASCADE"), primary_key=True)
    nums = Column(Integer, default=1)
    
    # 关系定义
    user = relationship("User", back_populates="books")
    book = relationship("Book", back_populates="users")
    
    __table_args__ = (
        CheckConstraint('nums > 0', name='check_nums_positive'),
    )

def init_models(engine):
    """初始化模型，创建所有表"""
    Base.metadata.create_all(engine)
