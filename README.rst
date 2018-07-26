Django Music Publisher
*******************************************************************************

.. image:: https://travis-ci.com/matijakolaric-com/django-music-publisher.svg?branch=master
    :target: https://travis-ci.com/matijakolaric-com/django-music-publisher

** Currennt version: 18.7b1**

This is a simple **Django app for original music publishers**. The app is 
released under `MIT license <LICENSE>`_ and is basically free. However, it uses
a paid external service for data validation and creation of CWR files, so using
it *may not be free*. Free 15-day demo licence for this service is available 
upon request. 

Introduction
===============================================================================

Introduction for Music Publishers
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are not a software developer, looking for a software solution for music
publishers, then everything beyond this point may be too technical for you.

This is a code repository. You may install this code on your computer or server
and modify it to suit your needs, or use it as is. It is not intended to be 
simple. It is intended to be customizable and extendable.

Introduction for Software Developers
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are looking for an open source code to make a custom software for a 
client who is a music publisher, and particularily if it includes Common Works
Registration (CWR) or even Electronic Batch Registration (EBR), and you have
never worked in this industry before, then you need to learn that things in 
this industry are extremely complicated. For large publishers, complicated is
financially much better than complex, which is much better than simple.

Use Case
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This app covers just a single use-case:
**one original publisher**, publishing **original musical works**.
(Original work is one that is not a modification of existing work.)
Situations with multiple writers are covered, but other publishers are ignored.
This still results in correct CWR files and enough data to acquire ISWC.

If you want to use it for exactly this purpose, just follow the standalone 
deployment instructions below.

Beyond
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are looking for a solution that covers much more territory, this may be 
an educational proof of concept, maybe even a good starting point for a custom 
development. It has very little dependecies and each model has an abstract 
parent, so including it in your project, even an existing one, should be pretty 
straightforward.

On the other hand, required data structure for a general publishing software is 
far more complex, even the part dealing with registrations. Everybody falls the
first time in designing the data structure, unless they have help. Yes, this is
a sales pitch.

CWR Developer Toolset
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_
covers basically all cases of CWR generation, validation and parsing. It is 
being constantly tested with most collecting societies and major publishers. 
There are various licencing packages.

This particular software uses two of the tools from the toolset, one for data
validation and one for generation of CWR files. It will work without these 
tools, but data will not be validated as CWR-compliant, and there will be no 
way to create CWR.

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

Publisher data will be required if you choose to go with your own CWR creator,
unless you change the structure significantly.

If that is the case, then all you may need is to set ``library`` and/or 
``label``, depending on your needs. 

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
