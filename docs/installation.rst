Installation
****************************************

Code repository for DMP can be found at https://github.com/matijakolaric-com/django-music-publisher.

Installation to a cloud
++++++++++++++++++++++++++++++++++++++++++++++++++++

DMP (Django-Music-Publisher) is based on Django Web Framework (https://djangoproject.org), and requires
Python 3 (https://python.org). It can be installed to a PC, but installing it into a cloud is highly recommended.

All three providers described below deploy DMP as a web application backed by
PostgreSQL. No background worker or scheduled CWR job is required. Exports
below the configured limit are generated automatically; larger exports are
started manually through the web interface or with ``generatecwr``. After the
first successful deployment, create a Django superuser and use the
environment variables described in `settings`_.

Digital Ocean
----------------------

**Provider and data jurisdiction:** DigitalOcean is a US company. You choose
the server region when creating the application; European regions include
Frankfurt, Amsterdam, and London, while DigitalOcean also operates regions
in the US and other countries. Hosting the application in Europe does not
remove the provider from US jurisdiction. The US CLOUD Act and other US laws
may therefore apply to data held by DigitalOcean, even when the selected
servers are in Europe.

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


2.1. In the first step, edit the plan and select Basic, then the cheapest plan, this is enough for publishers with up to several thousand works.

.. image:: /images/installation_do_1.png
   :width: 100%


2.2 Review the ``web`` environment variables. Leave the first three
variables from the deployment template as they are:

* ``DATABASE_URL`` is connected automatically to the ``default-db`` database.
  Its value is supplied by DigitalOcean and should not be replaced.
* ``ALLOWED_HOSTS`` is set to ``*``, which means everything listed in 
  ``Networking -> Domain``. Leave this value as it is.
* ``CSRF_TRUSTED_ORIGINS`` is set to ``${APP_URL}``, the most secure value. 
  Leave this value as it is.

For all remaining environment variables, use the explanations in `settings`_.

2.3 Select region closest to you.

2.4 Review and click on "create resources".

3. Installation takes several minutes. Once it is done, click on the
``console`` tab and enter:

.. code-block:: bash
         
    python manage.py migrate
    python manage.py createsuperuser

Then enter your user name and password (twice). You can leave e-mail empty, it is not used.

If you forget your login/password, you can use the console for adding a new superuser or change the password
with:

.. code-block:: bash
    
    python manage.py changepassword

Clever Cloud
----------------------

**Provider and data jurisdiction:** Clever Cloud is a French provider.
Its infrastructure is hosted across several regions in Europe and
internationally, using its own infrastructure and selected infrastructure
partners. Select the available European region in the Clever Cloud console
when creating the application. Clever Cloud states that its infrastructure
is designed to operate without dependence on extraterritorial laws. The US
CLOUD Act does not apply to Clever Cloud merely because the application is
hosted in Europe; however, the actual hosting region and any infrastructure
partner should still be checked for sensitive or regulated data.

Minimal cost depends on the selected application size and PostgreSQL add-on.

1. Create a Python application and a PostgreSQL add-on in the
`Clever Cloud Console <https://console.clever-cloud.com/>`_, then connect the
application to this Git repository. Deployments are started by pushing to
the configured branch.

2. Set the application environment variables. In addition to the values
listed in `settings`_, set:

   * ``CC_RUN_COMMAND``:
     ``waitress-serve --listen=0.0.0.0:9000 dmp_project.wsgi:application``
   * ``CC_PYTHON_MANAGE_TASKS``: ``migrate,collectstatic --noinput``

3. Connect the PostgreSQL add-on to the application so that
``DATABASE_URL`` is available. Optional S3-compatible file storage uses the
variables described in `S3 storage`_.

4. Review the application settings and deploy. Clever Cloud runs the
migrations and collects static files during the build. If either command
fails, the deployment fails.

5. Open a one-off console after the first successful deployment and enter:

.. code-block:: bash

    python manage.py createsuperuser

Scalingo
----------------------

**Provider and data jurisdiction:** Scalingo is a French provider. Its
standard regions and databases are hosted exclusively in France, including
the ``osc-fr1`` and ``osc-secnum-fr1`` regions, on 3DS Outscale
infrastructure. The US CLOUD Act does not directly apply to Scalingo as a
French provider, and selecting a French region avoids using a US hosting
region. Scalingo's contractual terms and any third-party services used with
the application should nevertheless be checked for the data being stored.

Minimal cost depends on the selected application size and PostgreSQL add-on.

1. Create a Python application and a PostgreSQL add-on in the
`Scalingo Dashboard <https://dashboard.scalingo.com/>`_, then connect the
application to this Git repository. Alternatively, create the application
and add its Git remote::

    scalingo create dmp
    git remote add scalingo git@ssh.osc-fr1.scalingo.com:dmp.git

2. Set the application environment variables. Scalingo supplies
``DATABASE_URL`` from the PostgreSQL add-on. Add the values listed in
`settings`_, including ``SECRET_KEY`` and the publisher and society
settings.

3. Deploy the configured branch::

    git push scalingo master

   Scalingo detects ``requirements.txt`` and starts the ``web`` process from
   ``Procfile``. The ``postdeploy`` process runs the database migrations
   after the new web process starts successfully.

4. Open a one-off console after the first successful deployment and enter:

.. code-block:: bash

    scalingo --app dmp run python manage.py createsuperuser

Use the application name and region shown by Scalingo. The example uses the
French ``osc-fr1`` region.

Custom installation
+++++++++++++++++++++++++++++++++++++++++++

For everything else, basic programming and/or system administration skills are required.

Start with `Deploying Django <https://docs.djangoproject.com/en/3.0/howto/deployment/>`_ documentation.

If you plan to use Django-Music-Publisher as one of the apps in an
existing Django project, install it from PyPI::

    pip install --upgrade django-music-publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``.
Run the usual Django migration and static-file commands from the directory
containing your project's ``manage.py``::

    python manage.py migrate
    python manage.py collectstatic
    python manage.py createsuperuser

Almost everything goes through the Django Admin. The only exception is
royalty calculation, which has to be added to ``urls.py``:

.. code:: python

    from music_publisher.royalty_calculation import RoyaltyCalculationView

    urlpatterns = [
        ...
        path('royalty_calculation/', RoyaltyCalculationView.as_view(), name='royalty_calculation'),
    ]

Experimental features (involving file system) may require additional work.

Good luck!


.. _settings:

Settings
+++++++++++++++++++++++++++++++++++++++++++++

There are several environment variables that need to be set, and several optional ones. Note that if invalid data is
entered or required data is not entered, deployment may fail and/or application may break down.

Secret key
-----------------------------------

Django requires ``SECRET_KEY`` to be set. It can be any random string. You can use https://miniwebtool.com/django-secret-key-generator/
to generate one, but do change it somewhat after pasting for complete security. Also make sure to encrypt it in the environment.

.. image:: /images/installation_do_2.png
   :width: 100%

Database
-----------------------------------

DMP uses SQLite by default and stores the database in ``db.sqlite3`` in the
project directory. This is convenient for local installations and small
single-user installations.

For production installations, PostgreSQL is recommended. Set
``DATABASE_URL`` to the connection URL supplied by your database provider,
for example::

    DATABASE_URL=postgres://username:password@host:5432/database

Run migrations after setting up or changing the database::

    python manage.py migrate

Security and trusted web addresses
-----------------------------------

These settings protect the application from requests sent to an unexpected
host or from an untrusted web address:

* ``ALLOWED_HOSTS`` - the host names that may be used to access the
  application. Enter host names without ``http://`` or ``https://``. 
* ``CSRF_TRUSTED_ORIGINS`` - the complete web addresses that are trusted to
  submit forms to the application. Include the scheme, such as
  ``https://example.com``.

Publisher-related settings
-----------------------------------

* ``PUBLISHER`` - Name of the publisher using Django-Music-Publisher, **required**
* ``PUBLISHER_IPI_NAME`` - Publisher's IPI *Name* Number, **required**
* ``PUBLISHER_CODE`` - Publisher's CWR Delivery code, defaults to ``000``, which is not accepted by CMOs, but may be accepted by (sub-)publishers.
* ``PUBLISHER_SOCIETY_PR`` - Publisher's performance collecting society (PRO) numeric code, required. See `Collective management organisations`_.

* ``PUBLISHER_IPI_BASE`` - Publisher's IPI *Base* Number, rarely used
* ``PUBLISHER_SOCIETY_MR`` - Publisher's mechanical collecting society (MRO) numeric code
* ``PUBLISHER_SOCIETY_SR`` - Publisher's synchronization collecting society numeric code, rarely used

For the list of codes, please have a look at societies.csv file in the music_publisher
folder of the code repository, or at the end of this document (`Collective management organisations`_).

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

DMP can store uploaded images and audio files either on the local file
system or in an S3-compatible object-storage service. File storage is
optional; it is only needed when using file uploads.

For local storage, set ``OPTION_FILES`` to ``1``. Files are stored in
``MEDIA_ROOT`` and are served under ``MEDIA_URL``. For example::

    OPTION_FILES=1
    MEDIA_ROOT=/var/lib/dmp/media
    MEDIA_URL=/media/

For DigitalOcean Spaces, AWS S3, or another S3-compatible provider, set
these four variables:

.. image:: /images/installation_do_f1.png
   :width: 100%

* ``S3_REGION`` (alias for ``AWS_S3_REGION_NAME``) and ``S3_BUCKET`` 
  (alias for ``AWS_STORAGE_BUCKET_NAME``), you get them when you set up your *Spaces*,
  and

.. image:: /images/installation_do_f2.png
   :width: 100%

* ``S3_ID`` (alias for ``AWS_ACCESS_KEY_ID``) and
  ``S3_SECRET`` (alias for ``AWS_SECRET_ACCESS_KEY``), you get them when you generate 
  your *Spaces* API key.

When all four S3 settings are present, DMP enables S3 storage automatically.
Set ``OPTION_FILES=1`` explicitly when you want to make this choice clear.
The AWS-style variable names may be used instead of the ``S3_*`` aliases:

* ``AWS_ACCESS_KEY_ID`` - access key for the storage service
* ``AWS_SECRET_ACCESS_KEY`` - secret access key for the storage service
* ``AWS_STORAGE_BUCKET_NAME`` - bucket or Space name
* ``AWS_S3_REGION_NAME`` - region identifier
* ``AWS_S3_ENDPOINT_URL`` - endpoint for non-AWS S3-compatible services

If you want to use AWS or some other S3 provider, the full list of settings is 
available 
`here <https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html>`_.


Other options
------------------------------------

* ``OPTION_FORCE_CASE`` - available options are ``upper``, ``title`` and ``smart``, 
  converting nearly all strings to UPPER CASE or Title Case or just UPPERCASE fields 
  to Title Case, respectively. If unset, everything is left as entered.

* ``OPTION_CWR_SYNC_WORK_LIMIT`` - maximum number of works for an export that
  is generated immediately while the export is created. Larger exports are
  saved as pending exports. The default is ``1000``.

* ``OPTION_CWR_WORKS_PER_FILE`` - maximum number of works in each generated
  CWR file when a large export is split into multiple files. The default is
  ``1000``.

* ``OPTION_CWR_NO_GENERATE_LINK`` - hides the link used to start pending CWR
  generation in the web interface. The default is ``False``, so the link is
  shown. Set it to ``1`` when pending exports should only be started with the
  ``generatecwr`` management command.

Background CWR generation
------------------------------------

Large exports are saved as pending exports when they exceed
``OPTION_CWR_SYNC_WORK_LIMIT``.

Pending exports can be processed manually through the web interface or by
running the ``generatecwr`` management command from the directory containing
``manage.py``::

    python manage.py generatecwr

The web-interface option for generating pending CWR files can be disabled by
setting ``OPTION_CWR_NO_GENERATE_LINK=1``. This is useful when pending
exports should only be started with the management command.

The command can be run periodically by cron, a systemd timer, or a scheduled
job provided by the hosting platform. For example, a cron entry that checks
for pending exports every five minutes might be::

    */5 * * * * cd /var/www/dmp && /var/www/dmp/.venv/bin/python manage.py generatecwr >> /var/log/dmp-generatecwr.log 2>&1

The five fields in ``*/5 * * * *`` mean that cron starts the command at
minute 0, 5, 10, 15, and so on, of every hour, every day. In other words,
cron checks for pending work every five minutes; it does not keep the command
running continuously. Each invocation processes the oldest pending export
that it can start and then exits.

Use the paths appropriate for the installation. Choose the interval according
to how quickly pending exports should be processed and how long generation
takes. A five-minute interval is a reasonable default. Use a shorter interval
for frequent smaller exports, or a longer interval if exports are large and
generation uses substantial resources. The command records when another
generation is already in progress, so overlapping invocations do not start a
second generation, but only one scheduler should normally be configured for
an installation.

If an export fails, the reason is saved with that export and it will not be
tried again automatically. After reading the error and making sure that the
problem has been fixed, ask the person who administers the installation to
retry it with::

    python manage.py generatecwr --force

The ``--force`` option means “try failed exports again”. It should only be
used after confirming that no other export is currently being generated.
Running it while another generation is in progress can create unnecessary
work or duplicate files. This command should only be run manually.

There is no way to force a failed CWR generation through the web interface.

Collective management organisations
++++++++++++++++++++++++++++++++++++++++++++++++

Following list contains official CWR codes for CMOs, to be entered in ``PUBLISHER_SOCIETY_PR``,
``PUBLISHER_SOCIETY_MR`` and rarely ``PUBLISHER_SOCIETY_SR`` environment variables.


.. csv-table::
   :file: societies.csv
   :widths: 10, 50, 40
   :header-rows: 0
