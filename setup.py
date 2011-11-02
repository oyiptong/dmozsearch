import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'pyramid_jinja2',
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='dmozsearch',
      version='0.0',
      description='dmozsearch',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Olivier Yiptong',
      author_email='olivier@olivieryiptong.com',
      url='',
      keywords='open directory dmoz search',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='dmozsearch',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = dmozsearch:main
      """,
      paster_plugins=['pyramid'],
      )

