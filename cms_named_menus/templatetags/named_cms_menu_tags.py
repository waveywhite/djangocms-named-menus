import json
from cms_named_menus import cache
import logging

from classytags.arguments import IntegerArgument, Argument, StringArgument
from classytags.core import Options
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import get_language
from menus.templatetags.menu_tags import ShowMenu

from cms_named_menus.nodes import get_nodes
from cms_named_menus.models import CMSNamedMenu


logger = logging.getLogger(__name__)

register = template.Library()


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

        menu_name = kwargs.pop('menu_name')

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
        
        arranged_nodes = cache.get(menu_name, lang)
        if arranged_nodes is None:
            logger.debug(u'Creating menu "%s %s"', menu_name, lang)
            try:
                named_menu = CMSNamedMenu.objects.get(name__iexact=menu_name).pages
            except ObjectDoesNotExist:
                logger.warn(u'Named menu "%s %s" not found', menu_name, lang)
                arranged_nodes = []
            else:
                nodes = get_nodes(context['request'], kwargs['namespace'], kwargs['root_id'])
                arranged_nodes = self.arrange_nodes(nodes, named_menu, namespace=kwargs['namespace'])
            cache.set(menu_name, lang, arranged_nodes)
        else:
            logger.debug(u'Fetched menu "%s %s" from cache', menu_name, lang)
        context.update({
            'children': arranged_nodes
        })
        return context

    def arrange_nodes(self, node_list, node_config, namespace=None):
        arranged_nodes = []
        for item in node_config:
            item.update({'namespace': namespace})
            node = self.create_node(item, node_list)
            if node is not None:
                arranged_nodes.append(node)
        return arranged_nodes

    def create_node(self, item, node_list):
        item_node = self.get_node_by_id(item['id'], node_list, namespace=item['namespace'])
        if item_node is None:
            return None

        if item_node.attr.get('cms_named_menus_generate_children', False):
            # Dynamic children
            # NOTE: We have to collect the children manually because get_node_by_id cleans the hierarchy
            child_items = [{ 'id' : node.id } for node in node_list if node.parent_id == item['id']]
            if len(child_items) == 0:
                nodes_json = json.dumps([{ node.id : node.title } for node in node_list], indent=4)
                logger.warn(u'Empty children for %s:\n%s', item_node.title, nodes_json)
                # Additional debugging output...
                from menus.menu_pool import menu_pool
                logger.warn('Menus in menu pool:\n%s', '\n'.join(menu_pool.menus.keys()))
        else:
            # Defined in the menu
            child_items = item.get('children', [])
        for child_item in child_items:
            child_node = self.get_node_by_id(child_item['id'], node_list, namespace=item['namespace'])
            if child_node is not None:
                item_node.children.append(child_node)
        return item_node

    def get_node_by_id(self, id, nodes, namespace=None):  # @ReservedAssignment
        final_node = None
        try:
            for node in nodes:
                if node.id == id and (namespace is None or node.namespace == namespace):
                    final_node = node
                    break
        except:
            logger.exception('Failed to find node')
        if final_node is not None:
            final_node.parent = None
            final_node.children = []
        return final_node


register.tag(ShowMultipleMenu)
