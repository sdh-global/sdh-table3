from setuptools import find_packages, setup

version = '2.0.0'

setup(
    name='sdh.table3',
    version=version,
    url='https://sdh.com.ua',
    author='Software Development Hub LLC',
    author_email='dev-tools@sdh.com.ua',
    description='Table rendering engine',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['sdh'],
    eager_resources=['sdh'],
    include_package_data=True,
    entry_points={},
    install_requires=['Django>=2.2', ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
