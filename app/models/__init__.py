# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 13:52
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py
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

    def delete(self):
        """从数据库删除对象"""
        db.session.delete(self)
        db.session.commit()
