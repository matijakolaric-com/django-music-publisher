Installation / Deployment and Configuration
*******************************************

Django-Music-Publisher can be installed/deployed as a stand-alone application, or used as a Python package.

Standalone Deployment
=====================

Depending on your needs and technical knowledge, there are several options here. They are listed below, starting with
the simplest option, which can be performed without any technical skills in under 5 minutes.

Deployment to Heroku (free tier)
--------------------------------

  Heroku is a cloud platform that lets companies build, deliver, monitor and scale apps — we're the fastest way to go
  from idea to URL, bypassing all those infrastructure headaches.

  -- https://www.heroku.com/what

Django-Music-Publisher can simply be deployed to a Free dyno (container) on Heroku with a free database with up to
10.000 rows. Depending on complexity of your metadata, this is enough for 500-1.000 musical works.

If you need more, plans costing between $9 and $16 per months will increase the limits to hundreds of thousands of
works. If you ever need more, this will no longer be the right software anyway.

See https://www.heroku.com/pricing for details.

You will have to sign up with Heroku at https://signup.heroku.com/ and verify your e-mail,
no payment information is required.

There are two ways to do it:

* Guided deployment, which uses a wizard that helps you fill out the deployment form, and
* Direct deployment, which does not, but takes you directly to the deployment form.

Guided Deployment to Heroku
+++++++++++++++++++++++++++

The author and maintainer of Django-Music-Publisher runs a
`professional support service <https://matijakolaric.com/dmp-prosupport/>`_,
providing automatic feature upgrades, security/bugfix updates, maintenance and user support.

.. figure:: /images/pre_wizard.png
   :width: 100%

It also provides a free (no registration required)
`pre-installation wizard <https://matijakolaric.com/dmp-preinstallation/>`_ that fills out the deployment
form on Heroku. A society compatibility list is provided. If your society or society combination
is not supported, use the next method.


Direct Deployment
+++++++++++++++++

.. raw:: html

    <p>First, you need to sign up with <a href="https://heroku.com">Heroku</a> and/or log in.
    Then press
    <a href="https://heroku.com/deploy?template=https://github.com/matijakolaric-com/django-music-publisher/tree/20.1.3">here</a>.</p>

.. figure:: /images/heroku.png
   :width: 100%

You will be taken directly to the deployment form. Please note that you must fill the form correctly, or
Django-Music-Publisher will not be deployed. This is by design.

See `Settings`_.

Other options - manual deployment
----------------------------------

Django-Music-Publisher is based on Django, which can be installed on Windows,
Mac and Linux PCs and servers. For more information, consult the official
`Deploying Django <https://docs.djangoproject.com/en/3.0/howto/deployment/>`_ documentation.

Installing as Python package (developers only)
===================================================================

If you plan to use Django-Music-Publisher as one of the apps in your Django project, there is nothing special about it::

    pip install --upgrade django_music_publisher

Add ``music_publisher.apps.MusicPublisherConfig`` to ``INSTALLED_APPS``, no URLs need to be added, as everything goes
through the Django Admin.

See `Settings`_.


Settings
===================================

Publisher-related settings
-----------------------------------

* ``PUBLISHER_NAME`` - Name of the publisher using Django-Music-Publisher, required
* ``PUBLISHER_CODE`` - Publisher's CWR Delivery code, without it CWR generation will not work.
* ``PUBLISHER_IPI_BASE`` - Publisher's IPI *Base* Number, rarely used
* ``PUBLISHER_IPI_NAME`` - Publisher's IPI *Name* Number, required

Affiliation settings
-----------------------------------

* ``PUBLISHER_SOCIETY_PR`` - Publisher's performance collecting society (PRO) numeric code, required
* ``PUBLISHER_SOCIETY_MR`` - Publisher's mechanical collecting society (MRO) numeric code
* ``PUBLISHER_SOCIETY_SR`` - Publisher's synchronization collecting society numeric code, rarely used

For the list of codes, please refer to the official CISAC documentation.

Agreement-related settings
-----------------------------------

* ``PUBLISHING_AGREEMENT_PUBLISHER_PR`` - Performance share transferred to the publisher, default is '0.5' (50%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_MR`` - Mechanical share transferred to the publisher, default is '1.0' (100%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_SR`` - Synchronization share transferred to the publisher, default is '1.0' (100%)
* ``REQUIRE_SAAN`` - Makes *Society-assigned agreement number* field required for controlled writers
* ``REQUIRE_PUBLISHER_FEE`` - Makes *Publisher Fee* field required for controlled writers
