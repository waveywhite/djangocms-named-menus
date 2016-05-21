# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''
from cms_named_menus.models import CMSNamedMenu

from cms.models.titlemodels import Title
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


def clear_cache(menu):
    key = 'cms_named_menu_%s' % menu.name
    cache.delete(key)

@receiver(post_save, sender=CMSNamedMenu, dispatch_uid='clear_cache_named_menu_saved')
def clear_cache_named_menu_saved(sender, instance, **kwargs):
    clear_cache(instance)
    
@receiver(post_save, sender=Title, dispatch_uid='clear_cache_title_saved')
def clear_cache_title_saved(sender, instance, **kwargs):
    page_id = instance.page.id
    for menu in CMSNamedMenu.objects.all():
        for page in menu.pages:
            if page['id'] == page_id:
                clear_cache(menu)
                break
    