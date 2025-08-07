# -*- coding:utf-8 -*-
from marshmallow import Schema, fields


class _PageContent:
    def __init__(self, page, items):
        self.page = page
        self.items = items


class Paginator:
    def __init__(self, query, page=1, per_page=10):
        page = int(page or 1)
        per_page = int(per_page or 10)
        self.page = 1 if page < 1 else page
        per_page = 10 if per_page < 1 else per_page
        self.per_page = 50 if per_page > 50 else per_page
        self.query = query
        self.page_query = query.limit(self.per_page).offset((self.page - 1) * self.per_page)

    def render_page(self):
        mobile_page = Page()

        total = self.query.count()
        pages = divmod(total, self.per_page)
        total_pages = pages[0] + 1 if pages[1] else pages[0]

        mobile_page.has_next = self.page < total_pages
        mobile_page.page = self.page
        mobile_page.per_page = self.per_page
        mobile_page.total = total
        mobile_page.total_pages = total_pages

        return _PageContent(mobile_page, self.page_query.all())


class Page:
    def __init__(self):
        self.page = 0
        self.per_page = 0
        self.has_next = False


class PageSchema(Schema):
    total = fields.Int(attribute='total')
    totalPages = fields.Int(attribute='total_pages')
    page = fields.Integer()
    perPage = fields.Integer(attribute='per_page')
    hasNext = fields.Boolean(attribute='has_next')
