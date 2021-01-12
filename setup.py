import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-music-publisher',
    version='21.1',
    author='Matija Kolarić',
    author_email='matijakolaric@users.noreply.github.com',
    license='MIT License',
    description=(
        'Software for managing music metadata, registration/licencing '''
        'of musical works and royalty processing.'),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://dmp.matijakolaric.com',
    project_urls={
        'Created by': 'https://matijakolaric.com',
        'Video Tutorials': 'https://www.youtube.com/watch?v=duqgzK3JitU&list=PLQ3e-DuNTFt-mwtKvFLK1euk5uCZdhCUP',
        'Documentation': 'https://django-music-publisher.readthedocs.io/',
        'Code Repository': 'https://github.com/matijakolaric-com/django'
                           '-music-publisher/',
    },
    packages=setuptools.find_packages(exclude=['dmp_project', 'docs']),
    install_requires=(
        'Django>=3.0,<3.1',
        'requests>=2.24.0',
    ),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    zip_safe=False,
)
