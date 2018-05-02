# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''


def contains_page(menu, page_id):
    for page in menu.pages:
        if page['id'] == page_id:
            return True
        for child in page.get('children', []):
            if child['id'] == page_id:
                return True
