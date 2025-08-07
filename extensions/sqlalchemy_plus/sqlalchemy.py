# -*- coding:utf-8 -*-
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy, BaseQuery, Model
import sqlalchemy as sa
from uuid import uuid1
from .schema import Paginator


def make_uuid():
    return str(uuid1()).replace('-', '').upper()


class CustomizedQuery(BaseQuery):
    def get_first(self):
        return super().filter_by(deleted=False).first()

    def get_by_id(self, id):
        return super().filter_by(id=id, deleted=False).first()

    def get_by_uuid(self, uuid):
        if uuid is None:
            return None
        return self.filter_by(uuid=uuid, deleted=False).first()

    def get_list(self, page=1, per_page=10):
        page = page or 1
        per_page = per_page or 10
        return Paginator(self, page, per_page).render_page()

    # def get_list(self, page=1, per_page=30):
    #     page = page or 1
    #     per_page = per_page or 30
    #     return Paginator(self, page, per_page).render_page()


class IdModel(Model):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(32), default=make_uuid)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, default=None)
    deleted = sa.Column(sa.Boolean, default=False)


class SQLAlchemyMixin:
    def save(self, obj):
        try:
            self.session.add(obj)
            self.session.commit()
            return obj
        except Exception as e:
            self.session.rollback()
            raise e

    def soft_delete(self, obj):
        try:
            obj.deleted = True
            obj.deleted_at = datetime.now()
            self.save(obj)
        except Exception as e:
            self.session.rollback()
            raise e

    def update(self, obj, params, save=True):
        try:
            for key in params.keys():
                if hasattr(obj, key):
                    setattr(obj, key, params[key])
            if save:
                return self.save(obj)
            else:
                return obj
        except Exception as e:
            self.session.rollback()
            raise e


class SQLAlchemyPlus(SQLAlchemy, SQLAlchemyMixin):
    pass
