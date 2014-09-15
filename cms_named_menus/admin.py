from django.contrib import admin
from .models import CMSNamedMenu
from cms.models.pagemodel import Page
from collections import OrderedDict
import json
from django.conf import settings
from menus.menu_pool import menu_pool


class CMSNamedMenuAdmin(admin.ModelAdmin):
    change_form_template = 'cms_named_menus/change_form.html'

    readoly_fields = ('pages_json',)

    def change_view(self, request, object_id, form_url='', extra_context={}):

        menu_pages = CMSNamedMenu.objects.get(id=object_id).pages

        extra_context = {
            'menu_pages': json.dumps(menu_pages),
            'cms_pages': self.serialize_navigation(request),
            'debug': settings.DEBUG,
        }

        return super(CMSNamedMenuAdmin, self).change_view(request, object_id, form_url, extra_context)

    def serialize_navigation(self, request):

        nodes = menu_pool.get_nodes(request)

        cleaned = []

        for node in nodes:
            node.children = []
            node.parent = []
            cleaned.append(node.__dict__)

        return json.dumps(cleaned)


admin.site.register(CMSNamedMenu, CMSNamedMenuAdmin)

