 # -*- coding:utf-8 -*-


class ApiNamespace(object):
    def __init__(self, namespace, api):
        """
        :param namespace: '/name_of_namespace'
        :param api: api object
        """
        self.api = api
        self.namespace = namespace

    def add_resource(self, resource, *urls, **kwargs):
        namespace_urls = []
        for url in urls:
            namespace_urls.append(self.namespace + url)
        self.api.add_resource(resource, *namespace_urls, **kwargs)


def init_app(app, **kwargs):
    pass
