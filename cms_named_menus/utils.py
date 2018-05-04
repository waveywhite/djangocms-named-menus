# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''
def contains_page(menu, url):
    for page in menu.pages:
        if page['url'] == url:
            return True
        for child in page.get('children', []):
            if child['url'] == url:
                return True

