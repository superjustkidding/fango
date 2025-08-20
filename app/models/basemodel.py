# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 16:42
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : basemodel.py
# @Software: PyCharm
from datetime import datetime
from app import db

class BaseModel(db.Model):
    """所有模型的基类，包含公共字段和方法"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)
    deleted = db.Column(db.Boolean, default=False)

    def save(self):
        """保存对象到数据库"""
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        """更新对象属性"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        db.session.commit()

    def delete(self):
        """软删除对象"""
        self.deleted = True
        self.deleted_at = datetime.now()
        db.session.commit()

    def restore(self):
        """恢复软删除的对象"""
        self.deleted = False
        self.deleted_at = None
        db.session.commit()

    def hard_delete(self):
        """从数据库永久删除对象"""
        db.session.delete(self)
        db.session.commit()
