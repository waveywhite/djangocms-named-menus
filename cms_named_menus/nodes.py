# -*- coding: utf-8 -*-
'''
Created on Jun 15, 2016

@author: jakob
'''
from django.contrib.auth.models import AnonymousUser
from menus.menu_pool import menu_pool


def anonymous_request(f):
    def decorator(request, *args, **kwargs):
        auth_user = None
        if request.user.is_authenticated():
            auth_user = request.user
            request.user = AnonymousUser()
        try:
            result = f(request, *args, **kwargs)
        finally:
            if auth_user is not None:
                request.user = auth_user
        return result

    return decorator


@anonymous_request
def get_nodes(request, namespace=None, root_id=None):
    # Django CMS >= 3.3
    renderer = menu_pool.get_renderer(request)

    all_nodes = renderer.get_nodes(namespace=namespace, root_id=root_id, breadcrumb=False)
    all_nodes = [node for node in all_nodes if not node.attr.get('cms_named_menus_hidden', False)]

    return all_nodes
