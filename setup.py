import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-music-publisher",
    version="0.0.2",
    author="Matija Kolarić",
    description="Django App for Music Publishers",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/matijakolaric-com/django-music-publisher/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
