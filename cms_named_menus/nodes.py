# -*- coding: utf-8 -*-
'''
Created on Jun 15, 2016

@author: jakob
'''
from django.contrib.auth.models import AnonymousUser
from menus.menu_pool import menu_pool


def anonymous_request(f):
    def decorator(request):
        auth_user = None
        if request.user.is_authenticated():
            auth_user = request.user
            request.user = AnonymousUser()
        try:
            result = f(request)
        finally:
            if auth_user is not None:
                request.user = auth_user
        return result
    return decorator

@anonymous_request
def get_nodes(request, namespace=None, root_id=None):
    if hasattr(menu_pool, 'get_renderer'):
        # Django CMS >= 3.3
        renderer = menu_pool.get_renderer(request)  # @UndefinedVariable
    else:
        renderer = menu_pool
    return renderer.get_nodes(request, namespace, root_id)