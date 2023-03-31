Installation and Upgrading
****************************************

Code repository for DMP can be found at https://github.com/matijakolaric-com/django-music-publisher.

Installation
++++++++++++++++++++++++++++++++++++++++++++++++++++

DMP (Django-Music-Publisher) is based on Django Web Framework (https://djangoproject.org), and requires
Python 3 (https://python.org). It can be installed to a PC, but installing int into a cloud is highly recommended.

Digital Ocean is the recommended provider.

Digital Ocean
----------------------

Minimal monthly cost is $5 for the application, $7 for the database, so $12 in total.
Optional $5 for file storage is only required for experimental features.

They usually give free credits that must be used within 60 days.


1. Click on the button below. (This is an affiliate link, providing you with free credits.)

.. raw:: html

    <a href="https://www.digitalocean.com/?refcode=b05ea0e8ec84&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge" target="_blank"><img src="https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg" alt="DigitalOcean Referral Badge" /></a>

2. Wizard

Once you have registered, click on the next button to start the installation wizard.

.. raw:: html

    <a href="https://cloud.digitalocean.com/apps/new?repo=https%3A%2F%2Fgithub.com%2Fmatijakolaric-com%2Fdjango-music-publisher%2Ftree%2Fmaster&refcode=b05ea0e8ec84" target="_blank">
        <img src="https://www.deploytodo.com/do-btn-blue.svg" alt="Deploy to DO">
    </a>


    2.1. Once you have registered, follow the wizard on Digital Ocean. In the first step, edit the plan and select Basic, then the cheapest plan, this is enough for publishers with up to several thousand works.

    .. figure:: /images/installation_do_1.png
       :width: 100%

    2.2 Edit ``web`` environment variables. See `settings`_ for details. Click on **SAVE**!!

    2.3 Select region closest to you.

    2.4 Review and click on "create resources".

3. Installation takes several minutes. Once it is done, click on the ``console`` tab and enter: 

.. code-block:: bash
         
python manage.py createsuperuser

Then enter your user name and password (twice). You can leave e-mail empty, it is not used.

If you forget your login/password, you can use the console for adding a new superuser or change the password
with:

.. code-block:: bash
    
python manage.py changepassword

Heroku
-----------------------

This is another provider with semi-automated deployment. The deployment to Heroku using the button below is NOT tested,
and issues with deployment will not be tested nor fixed.

.. raw:: html

    <a href="https://heroku.com/deploy?template=https%3A%2F%2Fgithub.com%2Fmatijakolaric-com%2Fdjango-music-publisher">
      <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
    </a>

    
Custom installation
-------------------------------------------------------------------------

For everything else, basic programming and/or system administration skills are required.

Start with `Deploying Django <https://docs.djangoproject.com/en/3.0/howto/deployment/>`_ documentation.

If you plan to use Django-Music-Publisher as one of the apps in your 
Django project, there is nothing special about it::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``. Almost everything goes
through the Django Admin. The only exception is royalty calculation, which has to be added to
``urls.py``

.. code:: python

    from music_publisher.royalty_calculation import RoyaltyCalculationView

    urlpatterns = [
        ...
        path('royalty_calculation/', RoyaltyCalculationView.as_view(), name='royalty_calculation'),
    ]

Experimental features (involving file system) may require additional work.

Good luck!


Settings
===================================

There are several environment variables that need to be set, and several optional ones. Note that if invalid data is
entered or required data is not entered, deployment may fail and/or application may break down.

Secret key
-----------------------------------

Django requires ``SECRET_KEY`` to be set. It can be any random string. You can use https://miniwebtool.com/django-secret-key-generator/
to generate one, but do change it somewhat after pasting for complete security.

Publisher-related settings
-----------------------------------

* ``PUBLISHER_NAME`` - Name of the publisher using Django-Music-Publisher, **required**
* ``PUBLISHER_IPI_NAME`` - Publisher's IPI *Name* Number, **required**
* ``PUBLISHER_CODE`` - Publisher's CWR Delivery code, defaults to ``000``, which is not accepted by CMOs, but may be accepted by (sub-)publishers.
* ``PUBLISHER_SOCIETY_PR`` - Publisher's performance collecting society (PRO) numeric code, required. See `Collective management organisations`_.

* ``PUBLISHER_IPI_BASE`` - Publisher's IPI *Base* Number, rarely used
* ``PUBLISHER_SOCIETY_MR`` - Publisher's mechanical collecting society (MRO) numeric code
* ``PUBLISHER_SOCIETY_SR`` - Publisher's synchronization collecting society numeric code, rarely used

For the list of codes, please have a look at societies.csv file in the music_publisher
folder of the code repository.

Agreement-related settings
-----------------------------------

These settings define the percentage of the manuscript share transferred to the publisher. 
The default is "London Split", where 50% of performance and 100% of mechanical and sync rights are transferred.

* ``PUBLISHING_AGREEMENT_PUBLISHER_PR`` - Performance share transferred to the publisher, default is '0.5' (50%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_MR`` - Mechanical share transferred to the publisher, default is '1.0' (100%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_SR`` - Synchronization share transferred to the publisher, default is '1.0' (100%)

Enter ``1.0`` for 100%, ``0.5`` for 50%, ``0.3333`` for 33.33%, etc.

S3 storage
------------------------------------

For Digital Ocean Spaces, you need to set up only four config (environment) variables. AWS and other S3 providers will
also work.

.. figure:: /images/installation_do_f1.png
   :width: 100%

* ``S3_REGION`` (alias for ``AWS_S3_REGION_NAME``) and ``S3_BUCKET`` 
  (alias for ``AWS_STORAGE_BUCKET_NAME``), you get them when you set up your *Spaces*,
  and

.. figure:: /images/installation_do_f2.png
   :width: 100%

* ``S3_ID`` (alias for ``AWS_ACCESS_KEY_ID``) and
  ``S3_SECRET`` (alias for ``AWS_SECRET_ACCESS_KEY``), you get them when you generate 
  your *Spaces* API key.

If you want to use AWS or some other S3 provider, the full list of settings is 
available 
`here <https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html>`_.


Other options
------------------------------------

* ``OPTION_FORCE_CASE`` - available options are ``upper``, ``title`` and ``smart``, 
  converting nearly all strings to UPPER CASE or Title Case or just UPPERCASE fields 
  to Title Case, respectively. If unset, everything is left as entered.

* ``OPTION_FILES`` - enables support for file uploads (audio files and images), using 
  local file storage (PC & VPS)

Collective management organisations
------------------------------------

Following list contains official CWR codes for CMOs, to be entered in ``PUBLISHER_SOCIETY_PR``,
``PUBLISHER_SOCIETY_MR`` and rarely ``PUBLISHER_SOCIETY_SR`` environment variables.


.. csv-table::
   :file: societies.csv
   :widths: 10, 50, 40
   :header-rows: 0

