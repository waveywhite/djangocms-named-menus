# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''
from django.conf import settings
from django.core.cache import cache


def _key(menu_name, lang):
    return 'cms_named_menu_%s_%s' % (menu_name, lang)

def get(menu_name, lang):
    key = _key(menu_name, lang)
    return cache.get(key, None)

def set(menu_name, lang, nodes):  # @ReservedAssignment
    key = _key(menu_name, lang)
    cache.set(key, nodes)

def delete(menu_name, lang=None):
    if lang is not None:
        key = _key(menu_name, lang)
        cache.delete(key)
    else:
        keys = [_key(menu_name, lang) for lang, _ in settings.LANGUAGES]
        cache.delete_many(keys)