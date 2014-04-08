import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'jsonschema',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'waitress',
    'warlock',
    'psycopg2',
    'SQLAlchemy',
    'zope.sqlalchemy',
]

setup(
    name='imio.webservice.json',
    version='0.0',
    description='imio.webservice.json',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='IMIO',
    author_email='support@imio.be',
    url='https://github.com/imio/',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="imiowebservicejson",
    entry_points="""\
    [paste.app_factory]
    main = imiowebservicejson:main
    """,
)
