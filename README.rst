Django CMS Named Menus
=====================

An extension for Django CMS that allows you to create multiple menus like Wordpress


Installation
------------

1. Install with pip ``pip install django-cms-named-menus``

2. Add ``cms_named_menus`` to INSTALLED_APPS


Usage
-----

After installation, place the ``{% show_named_menu 'MenuName' %}`` template tag where you want your menu to appear.

.. code::

  {% load named_cms_menu_tags %}

  <ul>
    {% show_named_menu "Main Menu" %}
  </ul>

Next, create your menu in the admin area using the drag and drop interface.

.. image:: ui.png


Settings
--------
The following settings can be changed by adding to your project's settings.py file:

1. Override the default cache duration for Named Menus, default = 3600 seconds

.. code::

  CMS_NAMED_MENUS_CACHE_DURATION = 3600


2. Set the application namespaces that can be used with Named Menus as a list, default is CMS pages only - as the page id will not be unique for other applications e.g. Aldryn NewsBlog etc. default = ['CMSMenu',]

.. code::

  CMS_NAMED_MENUS_NAMESPACES = ['CMSMenu',]






