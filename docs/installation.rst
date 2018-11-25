Installation
************

Django Music Publisher can be installed either as a Django app, or as a stand-alone project.

Installing the app
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

More information is available in this `video <https://www.youtube.com/watch?v=COi6LCzUTVQ&index=4&list=PLDIerrls8_JBuS82lC3qMSt-Yc-SKq8g3>`_.

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
