# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''
from cms_named_menus import cache
from cms_named_menus.models import CMSNamedMenu

from cms.models.titlemodels import Title
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


@receiver(post_save, sender=CMSNamedMenu, dispatch_uid='clear_cache_named_menu_saved')
def clear_cache_named_menu_saved(sender, instance, **kwargs):
    cache.delete(instance.name)
    
def _contains_page(menu, page_id):
    for page in menu.pages:
        if page['id'] == page_id:
            return True
        for child in page.get('children', []):
            if child['id'] == page_id:
                return True
            
@receiver(post_save, sender=Title, dispatch_uid='clear_cache_title_saved')
def clear_cache_title_saved(sender, instance, **kwargs):
    for menu in CMSNamedMenu.objects.all():
        if _contains_page(menu, instance.page.id):
            cache.delete(menu.name, instance.language)
    