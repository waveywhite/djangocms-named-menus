# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''

from django.conf import settings
from django.core.cache import cache

from cms_named_menus.models import CMSNamedMenu
from cms_named_menus.utils import contains_page
from cms_named_menus.settings import CACHE_DURATION


def _key(menu_slug, lang):
    return 'cms_named_menu_%s_%s' % (menu_slug, lang)


def get(menu_slug, lang):
    key = _key(menu_slug, lang)
    return cache.get(key, None)


def set(menu_slug, lang, nodes):  # @ReservedAssignment
    key = _key(menu_slug, lang)
    cache.set(key, nodes, CACHE_DURATION)


def delete(menu_slug, lang=None):
    delete_many([menu_slug], lang)


def delete_many(menu_slugs, lang=None):
    if len(menu_slugs) == 0:
        return
    keys = []
    if lang is not None:
        languages = [lang]
    else:
        languages = [lang for lang, _ in settings.LANGUAGES]
    for menu_slug in menu_slugs:
        keys.extend(_key(menu_slug, lang) for lang in languages)
    if len(keys) == 1:
        cache.delete(keys[0])
    else:
        cache.delete_many(keys)


def delete_by_page_id(page_id, lang=None):
    menu_slugs = []
    for menu in CMSNamedMenu.objects.all():
        if contains_page(menu, page_id):
            menu_slugs.append(menu.name)
    if menu_slugs:
        delete_many(menu_slugs, lang)
