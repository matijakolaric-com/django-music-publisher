import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-music-publisher',
    version='18.7',
    author='Matija Kolarić',
    license='MIT License',
    description='Django App for Music Publishers',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/matijakolaric-com/django-music-publisher/',
    packages=setuptools.find_packages(exclude=['dmp_project', 'docs']),
    classifiers=(
        'Environment :: Web Environment',
        'Framework :: Django :: 2.0',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ),
)
