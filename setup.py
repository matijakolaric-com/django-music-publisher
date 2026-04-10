import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-music-publisher",
    version="26.4a1",
    author="Matija Kolarić",
    author_email="matijakolaric@users.noreply.github.com",
    license="MIT License",
    description=(
        "Software for managing music metadata, batch registration "
        "of musical works, royalty processing and data exchange."
    ),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://django-music-publisher.readthedocs.io/",
    project_urls={
        "Created by": "https://matijakolaric.com",
        "Video Tutorials": "https://www.youtube.com/watch?v=Tyk6tYuFBrI"
        "&list=PLQ3e-DuNTFt-mwtKvFLK1euk5uCZdhCUP",
        "Documentation": "https://django-music-publisher.readthedocs.io/",
        "Code Repository": "https://github.com/matijakolaric-com/django"
        "-music-publisher/",
    },
    packages=setuptools.find_packages(exclude=["dmp_project", "docs"]),
    install_requires=(
        "Django>=5.2,<5.3",
        "boto3==1.38.0",
        "dj-database-url==3.1.2",
        "django-cleanup==9.0.0",
        "django-storages==1.14.6",
        "djangorestframework==3.16.0",
        "music-metadata-territories==24.12",
        "Markdown==3.7",
        "Pillow==11.2.1",
        "psycopg2-binary==2.9.10",
        "waitress==3.0.2",
        "whitenoise==6.9.0",
        "requests>=2.32.3",
    ),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 5.2",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    zip_safe=False,
)
