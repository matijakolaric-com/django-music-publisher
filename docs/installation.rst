Installation / Deployment and Configuration
*******************************************

Django-Music-Publisher can be installed/deployed as a stand-alone application, or used as a Python package.

Installing as Python package (developers only)
===================================================================

If you plan to use Django-Music-Publisher as one of the apps in your Django project, there is nothing special about it::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``, no URLs need to be added, as everything goes
through the Django Admin.

See `Settings`_.


Standalone Deployment
=====================

Depending on your needs and technical knowledge, there are several options here. They are listed below, starting with
the simplest option.

Deployment to Heroku
--------------------

This is the fastest and simplest option to deploy Django-Music-Publisher. One can use
the free tier of Heroku for testing and even for production up to ~1000 musical works.

.. raw:: html

    Simply press <a href="https://heroku.com/deploy?template=https://github.com/matijakolaric-com/django-music-publisher/tree/20">here</a>
    and you will be taken to Heroku. You need to register and then follow the instructions.

You will have to enter



You can only install this project on a system that has Python 3 pre-installed. Supported versions are 3.5, 3.6, 3.7, and
3.8.

Do::

    python3 -m venv dmp
    cd dmp
    source bin/activate
    git clone https://github.com/matijakolaric-com/django-music-publisher.git
    cd django-music-publisher
    pip install -r requirements.txt

On Windows: instead of ``source bin/activate``, run ``Scripts\activate``.

The next step is to create ``dmp_project/local_settings.py`` or set the
appropriate environment variables. ``SECRET_KEY``, ``ALLOWED_HOSTS``, and
``MUSIC_PUBLISHER_SETTINGS`` must be set.

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

.. raw:: html

   <iframe width="704" height="396" src="https://www.youtube-nocookie.com/embed/H1cVGXpM-3s/?list=PLDIerrls8_JBuS82lC3qMSt-Yc-SKq8g3" frameborder="0" allowfullscreen="1">&nbsp;</iframe>
   <p>The installation process for an older version can be seen here.</p>
   <p>This video is delivered from a cookie-less domain, which enhances your privacy, but some links in videos don't work.</p>

Installing as Django Module (developers only)
===============================================================================

If you plan to use Django-Music-Publisher as one of the apps in your Django project, there is nothing special about it::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``, no 
URLs need to be added, as everything goes through the Django Admin.


Settings
===============================================================================

You will have to add this to the settings, replace with your data.

.. code:: python

    MUSIC_PUBLISHER_SETTINGS = {

        'enforce_saan': True,  # Agr. # is required in many societies
        'enforce_publisher_fee': True,  # False for self-publishers
        'enforce_pr_society': True,  # Strictly not required, but good practice
        'enforce_ipi_name': True,  # Strictly not required, but good practice

        'work_id_prefix': 'TOP',  # Makes work and recording IDs somewhat unique
        
        'publisher_id': 'TOP',  # THE 2-4 letter CWR delivery publisher code
        'publisher_name': 'THE ORIGINAL PUBLISHER',  # the publisher name
        'publisher_ipi_name': '00000000199',  # IPI name number
        'publisher_ipi_base': 'I-000000001-9',  # IPI base number (rarely used)
        'publisher_pr_society': '52',  # Performing Rights Society Code
        'publisher_mr_society': '44',  # Mechanical Rights Society Code
        'publisher_sr_society': None,  # Sync Rights Society Code (rarely used)
    }

More information is available in this `video <https://www.youtube.com/watch?v=COi6LCzUTVQ&index=4&list=PLDIerrls8_JBuS82lC3qMSt-Yc-SKq8g3>`_. Please note that it refers to an earlier version.

.. raw:: html

   <iframe width="704" height="396" src="https://www.youtube-nocookie.com/embed/COi6LCzUTVQ/?list=PLDIerrls8_JBuS82lC3qMSt-Yc-SKq8g3" frameborder="0" allowfullscreen="1">&nbsp;</iframe>
   <p>The settings for an older version are explained here, some have been removed since. Please note that the support for multiple publishing entities in the US are gone.</p>
   <p>This video is delivered from a cookie-less domain, which enhances your privacy, but some links in videos don't work.</p>

Additional Societies
--------------------

The only optional setting is ``MUSIC_PUBLISHER_SOCIETIES``. In the default 
set-up, only 18 societies from 12 countries are present, as well as two 
administrative agencies. Here is the format::

    MUSIC_PUBLISHER_SOCIETIES = [
        ('101', 'SOCAN, Canada'),
        ('88', 'CMRRA, Canada'),
        ('10', 'ASCAP, United States'),
        ('21', 'BMI, United States'),
        ('71', 'SESAC Inc., United States'),
        ('34', 'HFA, United States'),
        ('707', 'Musicmark, Administrative Agency')]

.. _StandaloneDeployment:

Deployment on Heroku / Dokku / (any PaaS)
==============================================================================

``MUSIC_PUBLISHER_SETTINGS`` is required and too complex to be set as a config var.

One way to do this is to create a custom Django project in a private repository that uses the ``music_publisher`` app. Most files from ``dmp_project`` folder can be reused with no or minimal changes.

Another would be to use base64 encoding for this variable if your PaaS supports it.

DMP Guru
==============================================================================

`DMP Guru <https://dmp.guru/>`_ is a commercial hosting service for Django-Music-Publisher. Your instance of Django-Music-Publisher can be deployed in a minute.

You only need to provide basic data about the publisher (e.g. name, IPI name #, collecting society (or societies)) and it will figure out the correct settings. 

Your DMP instance will be properly maintained, regularly upgraded, data will be backed up daily, and you can export your data and move to another arrangement at any point.
