Django Music Publisher
*******************************************************************************

.. image:: https://travis-ci.com/matijakolaric-com/django-music-publisher.svg?branch=master
    :target: https://travis-ci.com/matijakolaric-com/django-music-publisher
.. image:: https://coveralls.io/repos/github/matijakolaric-com/django-music-publisher/badge.svg?branch=master
    :target: https://coveralls.io/github/matijakolaric-com/django-music-publisher?branch=master
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: ./LICENSE
.. image:: https://img.shields.io/pypi/v/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://img.shields.io/pypi/pyversions/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://img.shields.io/pypi/djversions/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://img.shields.io/pypi/status/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://img.shields.io/badge/contact-matijakolaric.com-d50000.svg
   :target: https://matijakolaric.com/z_contact/

This is a simple **Django app for original music publishers**. The app is 
released under `MIT license <LICENSE>`_ and is basically free. However, it uses
a paid external service for data validation and creation of CWR files, so using
it *may not be free*. Free 15-day demo licence for this service is available 
upon request. 

Introduction
===============================================================================

.. image:: https://matijakolaric-com.github.io/django-music-publisher/overview.png
    :target: https://matijakolaric-com.github.io/django-music-publisher/

Use Case
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This app is targeted at **single-entity original publishers**, publishing 
**original musical works**.
(Original work is one that is not a modification of an existing musical work.)

Multiple writers, both controlled and uncontrolled, are covered, but data on
other publishers (other original publishers, administrators and sub-publishers)
can not be entered. This is just enough data for acquiring ISWCs.

It is presumed that writers keep 50% of performing rights and the other 50%, 
as well as 100% of mechanical and sync goes to the original publisher.

Alternate titles and basic data on performing artists and just enough data for 
registration of library works, as well as full data about the first recording,
can be entered.

This translates to following CWR 2.1 transaction record types:

* NWR/REV,
* SPU (just one), SPT (just World),
* SWR, SWT (just World), PWR (including society-assigned agreement number), 
* OWR,
* ALT, 
* PER, 
* REC (single) and
* ORN (limited to library).

Beyond
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are looking for a solution that covers more territory, this may be 
an educational proof of concept, maybe even a good starting point for a custom 
development.

Please note that the limitations of this project are not chosen based on 
technical complexity of additional features, but due to the fact that beyond 
this point, the learning curve gets really steep, both for software developers 
and users.

Common Works Registration (CWR), or even the baby version of it, Electronic
Batch Registration (EBR), is usually the most time-consulimg part of any 
software project for music publishers. You may be interested in using external
REST API service for data validation, as well as generation and parsing of CWR 
files.

CWR Developer Toolset
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This particular software uses two simplest of the REST API tools from the 
`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_,
one for data validation and one for generation of CWR files.

Django Music Publisher app  works without these tools, but data will not be 
validated as CWR-compliant, and there will be no way to create CWR, unless you 
make your own. 

The latter could be solved with a template, but without the former, it would often not result in valid CWR files.

Installing the app
===============================================================================

If you want to install the `django_music_publisher` app, just use pip::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``, no 
URLs need to be added, as everything goes through the Django Admin.

You will have to add this to the settings, replace with your data.

.. code:: python

    MUSIC_PUBLISHER_SETTINGS = {
        'token': None,
        'validator_url': None,
        'generator_url': None,

        'publisher_id': 'TOP',  # THE 2-3 letter CWR delivery publisher code 
        'publisher_name': 'THE ORIGINAL PUBLISHER',  # the publisher name
        'publisher_ipi_name': '00000000199',  # IPI name number
        'publisher_ipi_base': 'I0000000393',  # IPI base number (rarely used)
        'publisher_pr_society': '052',  # Performing Rights Society Code
        'publisher_mr_society': '044',  # Mechanical Rights Society Code
        'publisher_sr_society': None,  # Sync Rights Society Code (rarely used)

        'library': 'THE FOO LIBRARY',  # Use only if you are in library music
        'label': 'FOO BAR MUSIC',  # Use only if you are also a label
    }

When you apply for a free 15-day demo licence, additional documentation will be
provided, as well as ``token``, ``validator_url``, and ``creator_url`` values.

Installing the project (standalone deployment)
===============================================================================

You can only install this project on a computer that has Python 3 preinstalled.
Supported versions are 3.5 and 3.6. It might work with other Python 3 versions,
but not with Python 2. It is advised you run this inside a virtual environment.

Do::

    python3 -m venv dmp

    cd dmp

    source bin/activate

    git clone git@github.com:matijakolaric-com/django-music-publisher.git

    cd django-music-publisher

    pip install -r requirements.txt

The next step is to create ``dmp_project/local_settings.py`` or edit 
``dmp_project/settings.py``. Regardless, ``SECRET_KEY`` and 
``MUSIC_PUBLISHER_SETTINGS`` (see above for details) must be set. Then::

    python manage.py migrate

    python manage.py createsuperuser

    python manage.py runserver

Then open the following link: http://localhost:8000/ and log in with
credentials you provided.

Societies
===============================================================================

The only optional setting is ``MUSIC_PUBLISHER_SOCIETIES``. In the default 
setup, only 12 societies from six countries are present. If you need to add
additional societies, do it with this setting (and not in the ``models.py``).

Societies the original publisher and writers are affiliated with, as well as
all societies whose acknowledgement files are being imported, must be present.

Validation and CWR Generation Service
===============================================================================

As stated above, this tool uses an external service for data validation and
generation of CWR files, which is a part of
`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_.

Free 15 day demo licence is available upon requests. Contact us through this 
`Contact Page <https://matijakolaric.com/z_contact/>`_. 

Walkthrough
===============================================================================

`Walkthrough <https://matijakolaric-com.github.io/django-music-publisher/>`_
is available in the ``docs`` folder.
