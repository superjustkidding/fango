# -*- coding:utf-8 -*-
class BusinessError(Exception):
    def __init__(self, error, description, status_code=400):
        self.error = error
        self.description = description
        self.status_code = status_code

    def __repr__(self):
        return 'Business : %s' % self.error

    def __str__(self):
        return '%s. %s' % (self.error, self.description)
