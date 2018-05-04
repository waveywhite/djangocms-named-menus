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
    url = None
    # path = None
    title = None
    children = []

    def __init__(self, node):
        self.id = node.id
        self.title = node.title
        self.url = node.get_absolute_url()


class CMSNamedMenuAdmin(admin.ModelAdmin):
    
    change_form_template = 'cms_named_menus/change_form.html'

    readoly_fields = ('pages_json',)

    list_display = ('name', 'slug')

    def change_view(self, request, object_id, form_url='', extra_context={}):

        # Get all Navigation nodes, excluding those set to 'cms_named_menus_hidden'
        all_nodes = get_nodes(request)
        node_dict = {node.get_absolute_url(): node.title for node in all_nodes}

        # Structure all navigation nodes, with parents
        available_pages = self.serialize_navigation(all_nodes)

        # Get the named menu nodes and dynamically update titles
        menu_pages = CMSNamedMenu.objects.get(id=object_id).pages
        named_menu_pages = self.get_menu_pages(menu_pages, node_dict)

        # Return the current and available nodes for selection
        extra_context = {
            'menu_pages': json.dumps(named_menu_pages, cls=LazyEncoder),
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
        # Clean node to be a simple title/url/children class
        cleaned_nodes = []
        for node in nodes:
            cleaned_node = SimpleNode(node)
            if node.children:
                cleaned_node.children = self.get_cleaned_node(node.children)
            cleaned_nodes.append(cleaned_node.__dict__)
        return cleaned_nodes


    def get_menu_pages(self, menu_pages, node_dict):
        # Recursively get the title for each page, or delete if removed
        for idx, page in enumerate(menu_pages):
            if page['url'] in node_dict:
                page['title'] = node_dict[page['url']]
            else:
                # Remove deleted nodes
                page = None

            # If not deleted, recursively get child nodes
            if page:
                # Get the page title for each child
                if 'children' in page:
                    page['children'] = self.get_menu_pages(page['children'], node_dict)

                menu_pages[idx] = page
            else:
                del menu_pages[idx]

        return menu_pages




admin.site.register(CMSNamedMenu, CMSNamedMenuAdmin)
