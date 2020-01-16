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

This is the fastest and simplest option, using the free tier of Heroku,
which is enough for 500-1.000  musical works, depending on their complexity.
If you need more, for $16 per month, the limit raises to hundreds of thousands, after which this tool is probably
no longer the right one.

.. raw:: html

    <p>First, you need to sign up with <a href="https://heroku.com">Heroku</a> and/or log in.
    Then press
    <a href="https://heroku.com/deploy?template=https://github.com/matijakolaric-com/django-music-publisher/tree/20">here</a>.</p>

You will be taken to the form you need to fill out correctly.

Select a name for your app, choose the region, and enter the Config Vars described next.

The first set is used for generating the superuser account. You should
change the password once you log in and delete these variables from Heroku dashboard.

*Please be careful, Heroku orders the fields alphabetically, e.g. USERNAME comes
after PASSWORD.*

* ``DJANGO_SUPERUSER_EMAIL`` - email address for the administrator account
* ``DJANGO_SUPERUSER_PASSWORD`` - password for the administrator account
* ``DJANGO_SUPERUSER_USERNAME`` - password for the administrator account

From the rest of the fields about your publishing entity, only these are required.

* ``PUBLISHER`` - the name of the publisher
* ``PUBLISHER_IPI_NAME`` - your IPI Name number
* ``PUBLISHER_SOCIETY_PR`` - numeric code of your collecting society

All Config Vars can be changed at any point in the Heroku Dashboard.

Please note that the data you enter must be valid, otherwise the installation
will fail. If you fail to get the values right, you may test the next option.

Professional support
---------------------------

The author and maintainer of Django-Music-Publisher runs a
`professional support service <https://matijakolaric.com/dmp-prosupport/>`_,
providing automatic upgrades and security/bugfix updates, maintenance and user support.

It also provides a free (no registration required) `pre-installation wizard <https://matijakolaric.com/dmp-preinstallation/>`_ that fills out the form
mentioned in the previous section with correct values.


Other options - manual deployment
----------------------------------

Django-Music-Publisher is based on Django, which can be installed on Windows,
Mac and Linux PCs and servers. For more information, consult the official
`Deploying Django <https://docs.djangoproject.com/en/3.0/howto/deployment/>`_ documentation.


Settings
____________________________________

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
* ``PUBLISHING_AGREEMENT_PUBLISHER_PR`` - Performance share transferred to the publisher, default is '0.5' (50%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_MR`` - Mechanical share transferred to the publisher, default is '1.0' (100%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_SR`` - Synchronization share transferred to the publisher, default is '1.0' (100%)

The last setting is a fairly complex one. The default works for most publishers, 50% of performance and 100% of
mechanical and 100% of sync is collected by the publisher.

Please contact your society or societies for details, as laws in some countries require
specific values, e.g. Netherlands.
