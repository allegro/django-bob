from setuptools import setup

setup(
    name='bob',
    description='A set of helper tags and templates for using bootstrap in django.',
    long_description="""
Bob is a library of templates, template tags, helper functions and form widgets
that make it easier to use the Twitter's Bootstrap framework with Django.
    """,
    version='1.0.0dev',
    license='BSD',
    url='https://bitbucket.org/thesheep/bob/',
    keywords='bootstrap django css html',
    packages=['bob', 'bob.templatetags'],
    install_requires=['distribute'],
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ],
)
