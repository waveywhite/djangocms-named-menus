from django.apps import AppConfig

class CMSNamedMenusConfig(AppConfig):
    name = 'cms_named_menus'
    verbose_name = "CMS Menus"

    def ready(self):
        import cms_named_menus.signals
