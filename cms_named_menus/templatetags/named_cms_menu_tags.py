from cms_named_menus import cache
import logging

from classytags.arguments import IntegerArgument, Argument, StringArgument
from classytags.core import Options
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import get_language
from menus.templatetags.menu_tags import ShowMenu

from autoslug.utils import slugify
from cms_named_menus.nodes import get_nodes
from cms_named_menus.models import CMSNamedMenu

logger = logging.getLogger(__name__)

register = template.Library()

NODES_REQUEST_CACHE_ATTR = "named_cms_menu_nodes_cache"


class ShowMultipleMenu(ShowMenu):
    name = 'show_named_menu'

    options = Options(
        StringArgument('menu_name', required=True),
        IntegerArgument('from_level', default=0, required=False),
        IntegerArgument('to_level', default=100, required=False),
        IntegerArgument('extra_inactive', default=0, required=False),
        IntegerArgument('extra_active', default=1000, required=False),
        StringArgument('template', default='menu/menu.html', required=False),
        StringArgument('namespace', default=None, required=False),
        StringArgument('root_id', default=None, required=False),
        Argument('next_page', default=None, required=False),
    )

    def get_context(self, context, **kwargs):

        # Get the name and derive the slug - for the cache key
        menu_name = kwargs.pop('menu_name')
        menu_slug = slugify(menu_name)

        context.update({
            'children': [],
            'template': kwargs.get('template'),
            'from_level': kwargs.get('from_level'),
            'to_level': kwargs.get('to_level'),
            'extra_inactive': kwargs.get('extra_inactive'),
            'extra_active': kwargs.get('extra_active'),
            'namespace': kwargs.get('namespace')
        })

        lang = get_language()

        request = context['request']
        namespace = kwargs['namespace']
        root_id = kwargs['root_id']

        # Try to get from Cache first
        arranged_nodes = cache.get(menu_slug, lang)

        # Create menu from Json if not
        if arranged_nodes is None:
            logger.debug(u'Creating menu "%s %s"', menu_slug, lang)
            named_menu = None
            arranged_nodes = []

            # Get by Slug or from Menu name - backwards compatible
            try:
                named_menu = CMSNamedMenu.objects.get(slug__exact=menu_slug).pages
            except ObjectDoesNotExist:
                try:
                    named_menu = CMSNamedMenu.objects.get(name__iexact=menu_name).pages
                except ObjectDoesNotExist:
                    logger.info(u'Named menu with name(slug): "%s (%s)" not found', menu_name, lang)

            # If we get the named menu, build the nodes
            if named_menu:
                # Try to get all the navigation nodes from the cache, or repopulate if not
                nodes = getattr(request, NODES_REQUEST_CACHE_ATTR, None)
                if nodes is None:
                    nodes = get_nodes(request, namespace, root_id)
                    # getting nodes is slow, cache on request object will
                    # speedup if more than one named menus are on the page
                    setattr(request, NODES_REQUEST_CACHE_ATTR, nodes)

                # Get the named menu nodes
                arranged_nodes = self.arrange_nodes(nodes, named_menu, namespace=namespace)
                if len(arranged_nodes) > 0:
                    logger.debug(u'Put %i menu "%s %s" to cache', len(arranged_nodes), menu_slug, lang)
                    cache.set(menu_slug, lang, arranged_nodes)
                else:
                    logger.debug(u'Don\'t cache empty "%s %s" menu!', menu_slug, lang)
        else:
            logger.debug(u'Fetched menu "%s %s" from cache', menu_slug, lang)

        context.update({
            'children': arranged_nodes
        })

        return context

    def arrange_nodes(self, node_list, node_config, namespace=None):
        arranged_nodes = []
        for item in node_config:
            node = self.create_node(item, node_list, namespace)
            if node is not None:
                arranged_nodes.append(node)
        return arranged_nodes


    def create_node(self, item, node_list, namespace=None):
        # Get Item node
        item_node = self.get_node_by_id(item['id'], node_list, namespace)
        if item_node is None:
            return None

        if item_node.attr.get('cms_named_menus_generate_children', False):
            # Dynamic children
            # NOTE: We have to collect the children manually because get_node_by_id cleans the hierarchy
            child_items = [{'id': node.id} for node in node_list if node.parent_id == item['id']]
            if len(child_items) == 0:
                logger.warn(u'Empty children for %s', item_node.title)
        else:
            # Child menu items defined in the menu
            child_items = item.get('children', [])

        # If child items, call recursively
        if child_items:
            for child_item in child_items:
                child_node = self.create_node(child_item, node_list, namespace)
                if child_node:
                    item_node.children.append(child_node)

        return item_node


    def get_node_by_id(self, id, nodes, namespace):  # @ReservedAssignment
        from copy import deepcopy
        final_node = None
        try:
            for node in nodes:
                if node.id == id and (not namespace or node.namespace == namespace):
                    final_node = node
                    break
        except:
            logger.exception('Failed to find node')
        if final_node is not None:
            final_node.parent = None
            final_node.children = []
            # Return Deepcopy which allows duplicated nodes throughout
            return deepcopy(final_node)

        return None


register.tag(ShowMultipleMenu)
