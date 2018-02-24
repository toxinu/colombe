#!/usr/bin/env python3
import os

from setuptools import setup
from setuptools import find_packages

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "src", "colombe", "__about__.py")) as f:
    exec(f.read(), about)

with open(os.path.join(base_dir, "README.md")) as f:
    long_description = f.read()

requires = [
    "Django==2.0.2",
    "django-cachalot==1.5.0",
    "celery==4.1.0",
    "click==6.7",
    "django-countries==5.1.1",
    "psycopg2-binary==2.7.4",
    "python-twitter==3.4",
    "django-redis==4.8.0",
    "restless==2.1.1",
    "social-auth-app-django==2.1.0 ",
]

setup(
    name=about["__title__"],
    version=about["__version__"],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    long_description=long_description,
    include_package_data=True,
    description=about["__summary__"],
    author=about["__author__"],
    author_email=about["__email__"],
    url=about["__uri__"],
    install_requires=requires,
    license=about["__license__"],
    entry_points={'console_scripts': ['colombe = colombe.cli:main']},
    extras_require={'dev': ['docker-compose==1.19.0'],
                    'tests': []},
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)'  # noqa
    ])
