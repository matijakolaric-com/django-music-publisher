Installation and Configuration
******************************

Django Music Publisher can be installed either as a Django app, or as a stand-alone project. 

There is a specialised commercial application PaaS `DMP Guru <https://dmp.guru/>`_ that simplifies the process for a moderate subscription fee.


Installing the App
===============================================================================

If you want to install the latest stable release of the 
`django_music_publisher` app, just use pip::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``, no 
URLs need to be added, as everything goes through the Django Admin.

Settings
++++++++

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


Django Music Publisher began as a proof of concept for a CWR Developer Toolset, a REST API service providing metadata validation and CWR generation, as well as syntax highlighting. 

.. _SyntaxHighlighting:

CWR Syntax Highlighting
+++++++++++++++++++++++

Basic data validation and CWR generation have since been added to Django Music Publisher code, but integrating CWR syntax highlighting still requires this external service. It is not required, and there is a free online `CWR Syntax Highlighting <https://matijakolaric.com/free/cwr-syntax-highlighter/>`_ tool with the exactly same functionality. Settings ``token`` and ``highlighter_url`` are used for this integration.

More information is available in this `video <https://www.youtube.com/watch?v=COi6LCzUTVQ&index=4&list=PLDIerrls8_JBuS82lC3qMSt-Yc-SKq8g3>`_. Please note that it refers to an earlier version.

.. _StandaloneDeployment:


Additional Societies
++++++++++++++++++++

The only optional setting is ``MUSIC_PUBLISHER_SOCIETIES``. In the default 
setup, only 18 societies from 12 countries are present, as well as two 
administrative agencies. If you need to add additional societies, do it with 
this setting (and not in the ``models.py``).

All societies the original publisher and all writers are affiliated with must be present.

Installing the Project (Standalone Deployment)
===============================================================================

You can only install this project on a system that has Python 3 preinstalled. Supported versions are 3.5, 3.6 and 3.7. It might work with other Python 3 versions, but not with Python 2. It is advised you run this inside a virtual environment.

Do::

    python3 -m venv dmp
    cd dmp
    source bin/activate
    git clone https://github.com/matijakolaric-com/django-music-publisher.git
    cd django-music-publisher
    pip install -r requirements.txt

The next step is to create ``dmp_project/local_settings.py`` or set the 
appropriate environment variables. ``SECRET_KEY``, ``ALLOWED_HOSTS``, and 
``MUSIC_PUBLISHER_SETTINGS`` (see above for details) must be set. 

Then::

    python manage.py migrate
    python manage.py createsuperuser

If you wish to add two predefined permission groups (recommended), run::
    
    python manage.py loaddata publishing_staff.json
    
For local installations, set ``DEBUG`` to ``True`` in 
``dmp_project/local_settings.py`` or as environment variable. Then run::

    python manage.py runserver

Then open the following link: http://localhost:8000/ and log in with
credentials you provided in a previous step. For instructions on permanent 
deployment, please use official 
`Django documentation <https://www.djangoproject.com/>`_.

Deployment on Heroku / Dokku
==============================================================================

``MUSIC_PUBLISHER_SETTINGS`` is required and too complex to be set as a config var. The recommended way to do this is to create a custom Django project in a private repository that uses the ``music_publisher`` app. Most files from ``dmp_project`` folder can be reused with no or minimal changes.


DMP Guru
==============================================================================

`DMP Guru <https://dmp.guru/>`_ is a commercial hosting service for Django Music Publisher. Your instance of Django Music Publisher can be deployed in a minute. 

You only need to provide basic data about the publisher (e.g. name, IPI name #, collecting society (or societies)) and it will figure out the correct settings. 

Your DMP instance will be properly maintained, regularily upgraded, data will be backed up daily, and you can export your data and move to another arrangement at any point.

