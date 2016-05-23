import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='troca',
    version='0.1',
    packages=['troca'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A web platform designed to support the creation and implementation of cultural projects.',
    long_description=README,
    url='http://troca.cc/',
    author='Troca',
    author_email='genitor06@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: X.Y',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.7.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "Django == 1.7.6",
        "Pillow == 2.7.0",
        "South == 1.0.2",
        "argparse == 1.2.1",
        "crispy-forms-foundation == 0.4.1",
        "django-ajax-selects == 1.3.6",
        "django-analytical == 0.21.0",
        "django-appconf == 1.0.1",
        "django-crispy-forms == 1.4.0",
        "django-easy-select2==1.2.12",
        "django-froala-editor==1.2.6",
        "django-guardian==1.2.5",
        "django-pure-pagination==0.2.1",
        "django-registration-redux==1.1",
        "django_social_share==0.3.0",
        "django-user-accounts==1.0.1",
        "django-userena==1.4.0",
        "easy-thumbnails==2.2",
        "gunicorn==19.3.0",
        "html2text == 2015.2.18",
        "mock == 1.0.1",
        "phileo == 1.3",
        "pytz == 2015.2",
        "six == 1.9.0",
        "wsgiref == 0.1.2",
        "django_feedback_form",
        "django-html_sanitizer",
        "beautifulsoup",
        "django_messages",
    ],
)
