Django Music Publisher
*******************************************************************************

.. image:: https://travis-ci.com/matijakolaric-com/django-music-publisher.svg?branch=master
    :target: https://travis-ci.com/matijakolaric-com/django-music-publisher

**Current version: 18.7b1**, the final release is scheduled for 2018-07-31.

This is a simple **Django app for original music publishers**. The app is 
released under `MIT license <LICENSE>`_ and is basically free. However, it uses
a paid external service for data validation and creation of CWR files, so using
it *may not be free*. Free 15-day demo licence for this service is available 
upon request. 

Introduction
===============================================================================

Music Publisher
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are not a software developer, looking for a software solution for music
publishers, then this may be the right thing for you, but you may need a 
software developer to implement.

Single Use Case
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This app covers just a single use-case:
**one original publisher**, publishing **original musical works**.
(Original work is one that is not a modification of an existing work.)

Multiple writers, both controlled and uncontrolled, are covered, but data on
other publishers (other original publishers, administrators and sub-publishers)
can not be entered. This still results in correct CWR files and enough data to 
acquire ISWCs.

Beyond
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are looking for a solution that covers much more territory, this may be 
an educational proof of concept, maybe even a good starting point for a custom 
development.

Common Works Registration (CWR), or even the baby version of it, Electronic
Batch Registration (EBR), is usually the most time-consulimg part of any 
software project for music publishers. You may be interested in using external
REST API service for data validation, as well as generation and parsing of CWR 
files.

CWR Developer Toolset
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This particular software uses two of the REST API tools from the 
`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_,
one for data validation and one for generation of CWR files.

It will work without these tools, but data will not be validated as 
CWR-compliant, and there will be no way to create CWR, unless you make your
own. The latter could be solved with a template, but without the former, it
would not result in valid CWR files.

Installing the app
===============================================================================

If you want to install the `music_publisher` Django app, just use pip::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``, no 
URLs need to be added, as everything goes through the Django Admin.

You will have to add this to the settings, replace with your data::

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

    cd django_music_publisher

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

Societies the original publisher and writers, as well as all societies whose
acknowledgement files are being imported, must be present.

Validation and CWR Generation Service
===============================================================================

As stated above, this tool uses an external service for data validation and
generation of CWR files, which is a part of
`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_

Free 15 day demo license is available upon requests. Contact us through this 
`Contact Page <https://matijakolaric.com/z_contact/>`_. 
