from setuptools import setup

# python setup.py sdist --formats=bztar

version = '2.0.11'
description = 'Yet Another Document Mapper (ODM) for MongoDB'
long_description = open('README.rst', 'rb').read().decode('utf8')


setup(
    name='yadm-xtix',
    version=version,
    description=description,
    long_description=long_description,
    author='XTIX Dev team',
    author_email='support@xtix.ai',
    url='https://github.com/',
    license='MIT',
    platforms='any',
    install_requires=[
        'pymongo>=3.7.0',
        'zope.dottedname',
        'python-dateutil',
        'pytz',
        'Faker',
    ],
    extras_require={
        'asyncio': [
            'motor>=2.0.0',
        ],
        'test': [
            'pytest',
            'pytest-asyncio',
            'pytest-cov',
            'coveralls'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Database',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],

    packages=['yadm', 'yadm.aio', 'yadm.fields', 'yadm.fields.money'],
)
