from setuptools import setup, find_packages

setup(
    name='django-bob',
    description='A set of helper tags and templates for using bootstrap in django.',
    long_description="""
Bob is a library of templates, template tags, helper functions and form widgets
that make it easier to use the Twitter's Bootstrap framework with Django.
    """,
    version='1.12.0',
    license='Apache 2',
    url='http://bob.readthedocs.org/',
    author='Radomir Dopieralski',
    author_email='devel@sheep.art.pl',
    keywords='bootstrap django css html',
    packages=find_packages(),
    install_requires=['distribute', 'django'],
    extras_require = {
        'reports': [
            'django-rq>=0.4.5',
            'rq>=0.3.7',
        ]
    },
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ],
)
