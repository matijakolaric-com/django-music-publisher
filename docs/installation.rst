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

This is the fastest and simplest option. One can use the free tier of Heroku for testing and even for production up to
~1000 musical works. This is the default.

.. raw:: html

    <p>Simply press <a href="https://heroku.com/deploy?template=https://github.com/matijakolaric-com/django-music-publisher/tree/20">here</a>
    and you will be taken to Heroku. You need to register and then follow the instructions.</p>


You should enter the name for your app, choose the region, and
enter several Config Vars.

The first set is used for generating the superuser account. You can and
change the password once you log in. You may as well delete these variables after the initial
installation in Heroku dashboard. *Please be careful, Heroku orders the fields alphabetically, e.g. USERNAME comes
after PASSWORD.*

* ``DJANGO_SUPERUSER_EMAIL`` - email address for the administrator account
* ``DJANGO_SUPERUSER_PASSWORD`` - password for the administrator account
* ``DJANGO_SUPERUSER_USERNAME`` - password for the administrator account

From the rest of the fields about your publishing entity, only these are required.

* ``PUBLISHER`` - the name of the publisher
* ``PUBLISHER_IPI_NAME`` - your IPI Name number
* ``PUBLISHER_SOCIETY_PR`` - numeric code of your collecting society

All Config Vars can be changed at any point in the Heroku Dashboard.

DMP.Guru
--------

The author and maintainer of Django-Music-Publisher offers professional maintenance of
Django-Music-Publisher instances deployed to Heroku as well as user support.

See https://dmp.guru for details.

Other options - manual deployment
----------------------------------

You can only install Django-Music-Publisher on a system that has Python 3 pre-installed.
Currently supported Python versions are 3.5, 3.6, 3.7, and 3.8. It is recommended to use it with
Python Virtual Environment.

For more information, consult the official
`Deploying Django <https://docs.djangoproject.com/en/3.0/howto/deployment/>`_ documentation.


Settings
____________________________________

Here is the excerpt from the settings, individual variables are described below.

.. code:: python

    PUBLISHER_NAME = os.getenv('PUBLISHER', 'DJANGO-MUSIC-PUBLISHER')
    PUBLISHER_CODE = os.getenv('PUBLISHER_CODE', '')

    PUBLISHER_IPI_BASE = os.getenv('PUBLISHER_IPI_BASE', None)
    PUBLISHER_IPI_NAME = os.getenv('PUBLISHER_IPI_NAME', '')

    PUBLISHER_SOCIETY_PR = os.getenv('PUBLISHER_SOCIETY_PR', None)
    PUBLISHER_SOCIETY_MR = os.getenv('PUBLISHER_SOCIETY_MR', None)
    PUBLISHER_SOCIETY_SR = os.getenv('PUBLISHER_SOCIETY_SR', None)

    PUBLISHER_AGREEMENT_SHARES = os.getenv('PUBLISHER_AGREEMENT_SHARES', '0.5,1,1')
    REQUIRE_SAAN = os.getenv('REQUIRE_SAAN', False)
    REQUIRE_PUBLISHER_FEE = os.getenv('REQUIRE_PUBLISHER_FEE', False)


Publisher-related settings
++++++++++++++++++++++++++++

* ``PUBLISHER_NAME`` - Name of the publisher using Django-Music-Publisher, required
* ``PUBLISHER_CODE`` - Publisher's CWR Delivery code
* ``PUBLISHER_IPI_BASE`` - Publisher's IPI *Base* Number, rarely used
* ``PUBLISHER_IPI_NAME`` - Publisher's IPI *Name* Number, required

Affiliation settings
++++++++++++++++++++++++++++
* ``PUBLISHER_SOCIETY_PR`` - Publisher's performance collecting society (PRO), required
* ``PUBLISHER_SOCIETY_MR`` - Publisher's mechanical collecting society (MRO)
* ``PUBLISHER_SOCIETY_SR`` - Publisher's synchronization collecting society, rarely used

Agreement-related settings
++++++++++++++++++++++++++++

* ``REQUIRE_SAAN`` - Makes *Society-assigned agreement number* field required for controlled writers
* ``REQUIRE_PUBLISHER_FEE`` - Makes *Publisher Fee* field required for controlled writers
* ``PUBLISHER_AGREEMENT_SHARES`` - Shares transferred to the publisher, comma separated performance, mechanical, sync

The last setting is a fairly complex one. The default works for most publishers, 50% of performance and 100% of
mechanical and 100% of sync is collected by the publisher.

Please contact your society or societies to check if your country laws require a certain value.

