import json

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from menus.menu_pool import menu_pool

from .models import CMSNamedMenu


class LazyEncoder(json.JSONEncoder):
    """Encodes django's lazy i18n strings.
        Used to serialize translated strings to JSON, because
        simplejson chokes on it otherwise. """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj

def anonymous_request(f):
    def decorator(self, request):
        auth_user = None
        if request.user.is_authenticated():
            auth_user = request.user
            request.user = AnonymousUser()
        try:
            result = f(self, request)
        finally:
            if auth_user is not None:
                request.user = auth_user
        return result
    return decorator

class CMSNamedMenuAdmin(admin.ModelAdmin):
    change_form_template = 'cms_named_menus/change_form.html'

    readoly_fields = ('pages_json',)

    def change_view(self, request, object_id, form_url='', extra_context={}):

        menu_pages = CMSNamedMenu.objects.get(id=object_id).pages

        extra_context = {
            'menu_pages': json.dumps(menu_pages),
            'available_pages': self.serialize_navigation(request),
            'debug': settings.DEBUG,
        }

        return super(CMSNamedMenuAdmin, self).change_view(request,
                                                          object_id,
                                                          form_url,
                                                          extra_context)

    @anonymous_request
    def serialize_navigation(self, request):

        nodes = menu_pool.get_nodes(request)

        cleaned = []

        for node in nodes:
            node.children = None
            node.parent = None
            cleaned.append(node.__dict__)

        return json.dumps(cleaned, cls=LazyEncoder)


admin.site.register(CMSNamedMenu, CMSNamedMenuAdmin)
