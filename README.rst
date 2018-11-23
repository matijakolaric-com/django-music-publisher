Django Music Publisher
******************************************************************************

.. image:: https://travis-ci.com/matijakolaric-com/django-music-publisher.svg?branch=master
    :target: https://travis-ci.com/matijakolaric-com/django-music-publisher
.. image:: https://img.shields.io/pypi/status/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://coveralls.io/repos/github/matijakolaric-com/django-music-publisher/badge.svg?branch=master
    :target: https://coveralls.io/github/matijakolaric-com/django-music-publisher?branch=master
.. image:: https://readthedocs.org/projects/django-music-publisher/badge/?version=latest
    :target: https://django-music-publisher.readthedocs.io/en/stable/?badge=latest
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/l/django-music-publisher.svg
   :target: https://github.com/matijakolaric-com/django-music-publisher/blob/master/LICENSE
.. image:: https://img.shields.io/pypi/v/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://img.shields.io/pypi/pyversions/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://img.shields.io/pypi/djversions/django-music-publisher.svg
    :target: https://pypi.org/project/django-music-publisher/
.. image:: https://img.shields.io/badge/home-matijakolaric.com-d50000.svg
   :target: https://matijakolaric.com/articles/2/

This is a simple **Django app for original music publishers**. The app is 
released under `MIT license <LICENSE>`_ and is basically free. At this point, 
it covers all the data required for batch (CWR) registrations of musical works, 
as well as basic data on agreements between the publisher and a writer.

An external (commercial) service can be used for complete data validation and 
CWR generation.

Introduction
===============================================================================

.. image:: https://matijakolaric-com.github.io/django-music-publisher/overview.png
    :target: https://matijakolaric-com.github.io/django-music-publisher/

Use Case
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This app is targeted at **single original publishers**, publishing 
**original musical works**.
It holds data on musical works, including alternate titles, songwriters, 
performing artists, first recordings, music library and albums. It allows 
data imports and exports.

Multiple writers, both controlled and uncontrolled, are covered, with minor 
limitations, but data on other publishers (other original publishers, 
administrators and sub-publishers) can not be entered.

A special **US** situation where an original publisher may have one entity for 
every of the three PROs is also covered.

It is presumed that writers own and collect 50% of performing rights and the 
other 50%, as well as 100% of mechanical and sync are owned and collected by 
the original publisher.

This translates to following CWR 2.x / 3.0 transaction record types:

======================================  =====================================
CWR 2.1 / 2.2                           CWR3.0
======================================  =====================================
NWR/REV                                 WRK, XRF
SPU, SPT (just World)                   SPU, SPT
SWR, SWT (just World), PWR, OWR         SWR, SWT (just World), PWR, OWR, OWT
ALT, PER, REC (single), ORN (only LIB)  ALT, PER, REC (single), ORN (only LIB) 
======================================  =====================================

Common Works Registration is used for batch registrations, although the actual
data validation and generation of CWR files uses an external commercial service.

Django Music Publisher can work without it, but data will not be validated as 
CWR-compliant, and there will be no way to export CWR.

Processing of CWR acknowledgement files works without the external service.

Processing of incoming royalty statements is on the roadmap, to be added later
in 2018. 

Beyond
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Please note that the limitations of this project are not chosen based on 
technical complexity of additional features, but due to the fact that beyond 
this point, the learning curve gets really steep, both for software developers 
and users.

CWR Validation, Generation and Syntax Highlighting
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This particular software uses three REST API tools from the 
`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_.

Even if you need a far more complex CWR, this project is still a good proof of
concept how well these tools work. Only CWR version 2.1 is fully supported.

CWR version 3.0 is under development (alpha).

Installing the App
===============================================================================

If you want to install the latest stable release of the 
`django_music_publisher` app, just use pip::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``, no 
URLs need to be added, as everything goes through the Django Admin.

You will have to add this to the settings, replace with your data.

.. code:: python

    MUSIC_PUBLISHER_SETTINGS = {
        'admin_show_publisher': False,  # Needed only in US version
        'admin_show_saan': True,  # Needed only if societies assign agr. #

        'enforce_saan': True,  # Agr. # is required in many societies
        'enforce_publisher_fee': True,  # False for self-publishers
        'enforce_pr_society': True,  # Strictly not required, but good practice
        'enforce_ipi_name': True,  # Strictly not required, but good practice

        'token': None,  # See below
        'validator_url': None,  # See below
        'generator_url': None,  # See below
        'highlighter_url': None,  # See below

        'work_id_prefix': 'TOP',  # Makes work IDs somewhat unique
        
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

For US publishers with entities in different PROs, define the "main" publisher
first, which is original publisher for affiliate writers in the respective PRO
and foreign societies. Then define publishers in other PROs.

.. code:: python

    MUSIC_PUBLISHER_SETTINGS = {
        'admin_show_publisher': True,  # Needed in US version
        'admin_show_saan': False,  # Not used in US

        'enforce_saan': False,  # Not used in US
        'enforce_publisher_fee': True,  # False for self-publishers
        'enforce_pr_society': True,  # Strictly not required, but good practice
        'enforce_ipi_name': True,  # Strictly not required, but good practice

        'token': None,  # See below
        'validator_url': None,  # See below
        'generator_url': None,  # See below
        'highlighter_url': None,  # See below

        'work_id_prefix': 'FOO',  # Makes work IDs somewhat unique
        
        'publisher_id': 'FOO',
        'publisher_name': 'FOO S MUSIC PUBLISHING',
        'publisher_ipi_name': '00000000199',
        'publisher_pr_society': '071',  # SESAC
        'publisher_mr_society': '034',  # HFA
        'publisher_sr_society': None,

        'us_publisher_override': {
            'ASCAP': {
                'publisher_id': 'FOOA',
                'publisher_name': 'FOO A MUSIC PUBLISHING',
                'publisher_ipi_name': '00000000493',
                'publisher_pr_society': '010',  # ASCAP
                'publisher_mr_society': '034',  # HFA
                'publisher_sr_society': None,
            },
            'BMI': {
                'publisher_id': 'FOOB',
                'publisher_name': 'FOO B MUSIC PUBLISHING',
                'publisher_ipi_name': '00000000395',
                'publisher_pr_society': '021',  # BMI 
                'publisher_mr_society': '044',  # HFA
                'publisher_sr_society': None,
            },
            'SESAC': None,  # Already defined, set to None
        },

        'library': 'FOO BAR MUSIC',  # Use only if you are in library music
        'label': 'FOO BAR MUSIC',  # Use only if you are also a label
    }

When you apply for a free 15-day demo licence for the external service that
validates the data and generates CWR, additional documentation will be
provided, as well as ``token``, ``validator_url``, ``creator_url`` and
``highlighter_url`` values.

Installing the project (standalone deployment)
===============================================================================

You can only install this project on a system that has Python 3 preinstalled.
Supported versions are 3.5, 3.6 and 3.7. 
It might work with other Python 3 versions, but not with Python 2. It is 
advised you run this inside a virtual environment.

Do::

    python3 -m venv dmp
    cd dmp
    source bin/activate
    git clone https://github.com/matijakolaric-com/django-music-publisher.git
    cd django-music-publisher
    pip install -r requirements.txt

The next step is to create ``dmp_project/local_settings.py`` or set the 
appropriate environment variables. ``SECRET_KEY``, ``ALLOWED_HOSTS``, and 
``MUSIC_PUBLISHER_SETTINGS`` (see above for details) must be set. Then::

    python manage.py migrate
    python manage.py createsuperuser

If you wish to add two predefined permission groups, run::
    
    python manage.py loaddata publishing_staff.json
    
Finally, run::

    python manage.py runserver

Then open the following link: http://localhost:8000/ and log in with
credentials you provided in a previous step. For instructions on permanent 
deployment, please use official 
`Django documentation <https://www.djangoproject.com/>`_.

Heroku
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
If you would like to try Django Music Publisher, Heroku is a good choice. The
free PostgreSQL tier can have up to 10.000 rows, which translates to about
1.000 works. 

Master branch, after it passes the CI, is deployed on Heroku automatically.
The following Config Vars are all that is required for that:

* ALLOWED_HOSTS set to the correct host name
* DATABASE_URL was set by PostgreSQL add-on
* TOKEN is set in order to use the external CWR generation, validation and
  syntax highlighting service.

* SECRET_KEY is not set, it is auto-generated on every deployment, which may 
  be fine for testing, but for production it should be set as well

Static files are automatically collected and served with Whitenoise. Waitress
is used instead of more usual uwsgi/gunicorn.

Societies
===============================================================================

The only optional setting is ``MUSIC_PUBLISHER_SOCIETIES``. In the default 
setup, only 18 societies from 12 countries are present, as well as two 
administrative agencies. If you need to add additional societies, do it with 
this setting (and not in the ``models.py``).

Societies the original publisher and writers are affiliated with, as well as
all societies whose acknowledgement files are being imported, must be present.

Validation and CWR Generation Service
===============================================================================

As stated above, this tool uses an external service for data validation and
generation of CWR files, which is a part of
`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_.

Free 15 day demo licence is available upon requests. Contact us through this 
`Contact Page <https://matijakolaric.com/z_contact/>`_. 

Demo
===============================================================================

A demo is available with some demo data. There are two versions, the US and the 
World version:

* `World Demo <https://dmp.matijakolaric.com/>`_
* `US Demo <https://dmp.matijakolaric.com/us/>`_

More information
===============================================================================

More information can be found at `<https://matijakolaric.com/articles/2/>`_.
