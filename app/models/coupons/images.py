# -*- coding: utf-8 -*-
# @Time    : 2025/8/19 15:05
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : images.py
# @Software: PyCharm


# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 16:03
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : coupons.py
# @Software: PyCharm

from app import db
from app.models import BaseModel

class Image(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(120), nullable=False)
    stored_name = db.Column(db.String(120), nullable=False, unique=True)
    file_path = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'original_name': self.original_name,
            'stored_name': self.stored_name,
            'url': self.url,
            'upload_date': self.upload_date.isoformat()
        }
