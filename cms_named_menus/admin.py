import json

from django.utils.functional import Promise
from django.utils.encoding import force_unicode

from django.conf import settings
from django.contrib import admin

from cms_named_menus.models import CMSNamedMenu
from cms_named_menus.nodes import get_nodes


class LazyEncoder(json.JSONEncoder):
    """Encodes django's lazy i18n strings.
        Used to serialize translated strings to JSON, because
        simplejson chokes on it otherwise. """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj


class SimpleNode(object):
    id = None
    title = None
    children = []

    def __init__(self, node):
        self.id = node.id
        self.title = node.title


class CMSNamedMenuAdmin(admin.ModelAdmin):
    change_form_template = 'cms_named_menus/change_form.html'

    readoly_fields = ('pages_json',)

    list_display = ('name', 'slug')

    def change_view(self, request, object_id, form_url='', extra_context={}):
        available_pages = self.serialize_navigation(get_nodes(request))
        menu_pages = CMSNamedMenu.objects.get(id=object_id).pages
        extra_context = {
            'menu_pages': json.dumps(menu_pages),
            'available_pages': json.dumps(available_pages, cls=LazyEncoder),
            'debug': settings.DEBUG,
        }
        return super(CMSNamedMenuAdmin, self).change_view(request, object_id, form_url, extra_context)

    def serialize_navigation(self, all_nodes):
        # Recursively convert nodes to simple nodes
        cleaned = []
        for node in all_nodes:
            if not node.parent_id:
                cleaned_node = self.get_cleaned_node([node])
                cleaned += cleaned_node

        return cleaned

    def get_cleaned_node(self, nodes):
        # Clean node to be a simple title/id/children class
        cleaned_nodes = []
        for node in nodes:
            cleaned_node = SimpleNode(node)
            if node.children:
                cleaned_node.children = self.get_cleaned_node(node.children)
            cleaned_nodes.append(cleaned_node.__dict__)
        return cleaned_nodes


admin.site.register(CMSNamedMenu, CMSNamedMenuAdmin)
