# -*- coding: utf-8 -*-
# @Time    : 2025/8/19 14:46
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : saveimage.py
# @Software: PyCharm

import os
import uuid
from werkzeug.utils import secure_filename
from app.models.coupons.images import Image
from config import load_config

config = load_config()

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config['ALLOWED_EXTENSIONS']


def generate_filename(original_filename):
    ext = original_filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


def save_image(file):
    """保存单个图片并返回数据库对象"""
    if not allowed_file(file.filename):
        return None, "Invalid file type"

    original_name = secure_filename(file.filename)
    stored_name = generate_filename(original_name)

    # 确保上传目录存在
    os.makedirs(config['UPLOAD_FOLDER'], exist_ok=True)
    save_path = os.path.join(config['UPLOAD_FOLDER'], stored_name)

    # 保存文件
    file.save(save_path)

    # 生成访问URL
    image_url = f"{config['BASE_URL']}/uploads/{stored_name}"

    # 创建数据库对象
    image = Image(
        original_name=original_name,
        stored_name=stored_name,
        file_path=save_path,
        url=image_url
    )

    return image, None

