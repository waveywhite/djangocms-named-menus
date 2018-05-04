# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''
from cms.models.pagemodel import Page
from cms.models.titlemodels import Title
from cms_named_menus import cache
from cms_named_menus.models import CMSNamedMenu
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch.dispatcher import receiver


cache_url = None
cache_inst_id = None


@receiver(post_save, sender=CMSNamedMenu, dispatch_uid='clear_cache_named_menu_saved')
def clear_cache_named_menu_saved(sender, instance, **kwargs):
    cache.delete(instance.slug)


@receiver(post_delete, sender=CMSNamedMenu, dispatch_uid='clear_cache_named_menu_deleted')
def clear_cache_named_menu_deleted(sender, instance, **kwargs):
    cache.delete(instance.slug)


@receiver(post_save, sender=Page, dispatch_uid='clear_cache_page_post_save')
def clear_cache_page_post_save(sender, instance, **kwargs):
    # Only delete from cache if page has a title set i.e. not a page_type
    if instance.title_set.exists():
        url = instance.get_absolute_url()
        cache.delete_by_page_url(url)


@receiver(pre_save, sender=Title, dispatch_uid='clear_cache_title_pre_save')
def clear_cache_title_pre_save(sender, instance, **kwargs):
    # Set cache urls for before/after comparison
    global cache_url, cache_inst_id
    # Only check for changes if the instance already exists
    if instance.pk:
        cache_url = instance.page.get_absolute_url()
        cache_inst_id = instance.id
        cache.delete_by_page_url(cache_url)
    else:
        cache_url = None
        cache_inst_id = None


@receiver(post_save, sender=Title, dispatch_uid='clear_cache_title_post_save')
def clear_cache_title_post_save(sender, instance, **kwargs):
    global cache_url, cache_inst_id
    if cache_inst_id and instance.id == cache_inst_id:
        new_url = sender.objects.get(id=instance.id).page.get_absolute_url()
        if cache_url != new_url:
            cache.update_changed_menu(cache_url, new_url)
    else:
        cache_url = None
        cache_inst_id = None


@receiver(pre_delete, sender=Title, dispatch_uid='clear_cache_title_deleted')
def clear_cache_title_deleted(sender, instance, **kwargs):
    try:
        abs_url = instance.page.get_absolute_url()
        cache.delete_by_page_url(abs_url, instance.language)
    except:
        pass
