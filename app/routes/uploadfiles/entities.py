# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:01
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : entities.py.py
# @Software: PyCharm

import os
from app import db
from lib.ecode import ECode
from app.utils.validation import BusinessValidationError
from .saveimage import save_image


class SingleEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user

    def single_upload(self, data):
        if 'file' not in data.files:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        file = data.files['file']

        if file.filename == '':
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        image, error = save_image(file)
        if error:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        try:
            db.session.add(image)
            db.session.commit()
            return {
                'message': 'File uploaded successfully',
                'image': image.to_dict()
                 }, ECode.SUCC
        except Exception as e:
            # 删除已保存的文件
            if os.path.exists(image.file_path):
                os.remove(image.file_path)
            raise BusinessValidationError('name already exists', ECode.INTER)


class BulkEntity:
    def __init__(self, current_user):
        self.current_user = current_user

    def bulk_upload(self, data):
        if 'files' not in data.files:
            raise BusinessValidationError("Permission denied", ECode.ERROR)
        files = data.files.getlist('files')
        if not files or files[0].filename == '':
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        results = []
        errors = []

        for file in files:
            image, error = save_image(file)
            if error:
                errors.append({'filename': file.filename, 'error': error})
                continue
            try:
                db.session.add(image)
                results.append(image)
            except Exception as e:
                # 删除已保存的文件
                if os.path.exists(image.file_path):
                    os.remove(image.file_path)
                errors.append({'filename': file.filename, 'error': str(e)})

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise BusinessValidationError('name already exists', ECode.INTER)

        response = {
            'message': f'Uploaded {len(results)} files, {len(errors)} failed',
            'successful_uploads': [img.to_dict() for img in results],
            'failed_uploads': errors
        }

        return response, ECode.SUCC



