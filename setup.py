import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt')) as f:
    version = f.read().strip()

requires = [
    'jsonschema',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'waitress',
    'warlock',
    'imio.dataexchange.core',
    'imio.dataexchange.db',
    'imio.amqp',
    'configparser',
    'cornice',
    'cornice_swagger',
    'requests',
]

setup(
    name='imio.webservice.json',
    version=version,
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
    extras_require={
        'test': [
            'mock',
            'webtest',
        ],
        'dev': [
            'ipdb',
        ],
    },
    entry_points="""\
    [paste.app_factory]
    main = imiowebservicejson:main
    [console_scripts]
    document_publisher = imiowebservicejson.scripts.documentpublisher:main
    request_read_handler = imiowebservicejson.scripts.requesthandler:read_handler
    request_write_handler = imiowebservicejson.scripts.requesthandler:write_handler
    request_error_handler = imiowebservicejson.scripts.requesterror:main
    file_cleanup = imiowebservicejson.scripts.cleanup:main
    """,
)
