import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-music-publisher',
    version='20.1.4',
    author='Matija Kolarić',
    author_email='matijakolaric@users.noreply.github.com',
    license='MIT License',
    description='Django app/project for original music publishers',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://django-music-publisher.readthedocs.io',
    packages=setuptools.find_packages(exclude=['dmp_project', 'docs']),
    install_requires=(
        'Django>=3.0.5,<3.1',
        'requests>=2.20.0',
    ),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    zip_safe=False,
)
