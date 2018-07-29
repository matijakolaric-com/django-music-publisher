import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-music-publisher',
    version='18.7',
    author='Matija Kolarić',
    author_email='i@matijakolaric.com',
    license='MIT License',
    description='Django App for Music Publishers',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/matijakolaric-com/django-music-publisher/',
    packages=setuptools.find_packages(exclude=['dmp_project', 'docs']),
    include_package_data=True,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'Intended Audience :: Music Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ),
    zip_safe=False,
)
