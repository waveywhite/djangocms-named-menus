# Generated by Django 2.2.12 on 2020-05-22 20:39

import collections
from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_named_menus', '0007_auto_20190520_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cmsnamedmenu',
            name='pages',
            field=jsonfield.fields.JSONField(blank=True, default=[], load_kwargs={'object_hook': collections.OrderedDict}, null=True),
        ),
    ]
