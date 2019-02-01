# /usr/bin/env python
import codecs
import os
from setuptools import setup, find_packages

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

setup(
    name='django-cms-named-menus',
    version='0.2.1',
    description='Allows you to add named menus like Wordpress',
    long_description=read(os.path.join(os.path.dirname(__file__), 'README.rst')),
    author='Ryan Bagwell',
    author_email='ryan@ryanbagwell.com',
    license='BSD',
    url='https://github.com/ryanbagwell/django-cms-named-menus/',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Django>=1.6',
        'django-classy-tags',
        'django-cms>=3.3',
        'jsonfield>=1.0.0',
        'django-autoslug>=1.7.2',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
