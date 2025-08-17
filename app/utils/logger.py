# -*- coding:utf-8 -*-
from logzero import setup_logger
from logging import INFO


def create_logger(name, max_bytes=int(10 * 1e6), backup_count=3):
    return setup_logger(name=name,
                        logfile='log/{0}.log'.format(name),
                        level=INFO,
                        maxBytes=max_bytes,
                        backupCount=backup_count)
