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
    delete_many([menu_name], lang)

def delete_many(menus_names, lang=None):
    if len(menus_names) == 0:
        return
    keys = []
    if lang is not None:
        languages = [lang]
    else:
        languages = [lang for lang, _ in settings.LANGUAGES]
    for menu_name in menus_names:
        keys.extend(_key(menu_name, lang) for lang in languages)
    if len(keys) == 1:
        cache.delete(keys[0])
    else:
        cache.delete_many(keys)
