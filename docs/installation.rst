Installation, Configuration and Updating
****************************************

Django-Music-Publisher (DMP) can be installed/deployed as a stand-alone application, or used as a Python package.

Standalone Deployment
=====================

Depending on your needs and technical knowledge, there are several options. They are listed below, starting with
the simplest option, which can be performed without any technical skills in under 5 minutes.

Deployment to Heroku (free tier)
--------------------------------

  Heroku is a cloud platform that lets companies build, deliver, monitor and scale apps — we're the fastest way to go
  from idea to URL, bypassing all those infrastructure headaches.

  -- https://www.heroku.com/what

Django-Music-Publisher can simply be deployed to a *Free dyno* on Heroku with a free *Dev* database with up to
10.000 rows. Depending on complexity of your metadata, this is enough for up to 1.000 musical works.

.. note::
    With *Hobby Basic* database ($9 per month), the database limit raises to 10.000.000 rows, which should be more
    than enough for any user od DMP.
    See `Heroku prices <https://www.heroku.com/pricing>`_ for more information.

You will have to sign up with Heroku at https://signup.heroku.com/ and verify your e-mail,
no payment information is required.

There are two ways to do it:

* Guided deployment, which uses a wizard that helps you fill out the deployment form, and
* Direct deployment, which does not, but takes you directly to the deployment form.

Guided Deployment to Heroku
+++++++++++++++++++++++++++

The author and maintainer of Django-Music-Publisher provides a
`pre-installation wizard <https://matijakolaric.com/dmp-preinstallation/>`_,
which will guide you through the deployment process.

.. figure:: /images/pre_wizard.png
   :width: 100%

There is also a compatibility list for many collective management organizations. If your
CMO or combination of CMOs is not supported, you can use the next method.

Direct Deployment
+++++++++++++++++

First, you need to sign up with `Heroku <https://heroku.com>`_ and/or log in.
Then click `here <https://heroku.com/deploy?template=https://github.com/matijakolaric-com/django-music-publisher/>`_.
This will deploy the latest code in |version| branch.

.. figure:: /images/heroku.png
   :width: 100%

You will be taken directly to the deployment form. Please note that you must fill the form correctly, or
Django-Music-Publisher will not be deployed. This is by design.

See `Settings`_ for more information.

Updating DMP on Heroku
++++++++++++++++++++++

There are three reasons for udating DMP: 

* if there is a security issue with the version you installed,
* if there is a bug that affects you, or
* if you need some features from the newer version.

While installation to Heroku is really simple, updating requires some technical knowledge. The simplest way to update is to install `Heroku CLI (command line interface) <https://devcenter.heroku.com/articles/heroku-cli>`_. It can be installed on Windows, Mac and Linux.

Then you log in, clone the repository, enter the folder, add a new remote and push:

.. code-block:: bash

   $ heroku login
   $ git clone https://github.com/matijakolaric-com/django-music-publisher.git
   $ cd django-music-publisher/
   django-music-publisher$ heroku git:remote --app yourapp 
   django-music-publisher$ git push heroku master
   
If you are upgrading from a version older than 20.7, you may need to delete an old buildpack, which can be found in Heroku dashboard in the ``Settings`` tab.

Other options - manual deployment (developers or system engineers)
--------------------------------------------------------------------------------

Django-Music-Publisher is based on Django, which can be installed on Windows,
Mac and Linux PCs and servers. For more information, consult the official
`Deploying Django <https://docs.djangoproject.com/en/3.0/howto/deployment/>`_ documentation.

Installing as Python package (developers only)
===================================================================

If you plan to use Django-Music-Publisher as one of the apps in your Django project, there is nothing special about it::

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

There are several required `settings`_.

.. _settings:

Settings
===================================

Publisher-related settings
-----------------------------------

* ``PUBLISHER_NAME`` - Name of the publisher using Django-Music-Publisher, required
* ``PUBLISHER_CODE`` - Publisher's CWR Delivery code, without it CWR generation will not work.
* ``PUBLISHER_IPI_BASE`` - Publisher's IPI *Base* Number, rarely used
* ``PUBLISHER_IPI_NAME`` - Publisher's IPI *Name* Number, required
* ``PUBLISHER_SOCIETY_PR`` - Publisher's performance collecting society (PRO) numeric code, required
* ``PUBLISHER_SOCIETY_MR`` - Publisher's mechanical collecting society (MRO) numeric code
* ``PUBLISHER_SOCIETY_SR`` - Publisher's synchronization collecting society numeric code, rarely used

For the list of codes, please refer to the official CISAC documentation. Society codes must
be entered *without* leading zeros.

Agreement-related settings
-----------------------------------

* ``PUBLISHING_AGREEMENT_PUBLISHER_PR`` - Performance share transferred to the publisher, default is '0.5' (50%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_MR`` - Mechanical share transferred to the publisher, default is '1.0' (100%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_SR`` - Synchronization share transferred to the publisher, default is '1.0' (100%)

Other settings
------------------------------------
* ``REQUIRE_SAAN`` - Makes *Society-assigned agreement number* field required for controlled writers
* ``REQUIRE_PUBLISHER_FEE`` - Makes *Publisher Fee* field required for controlled writers
* ``ENABLE_NOTES`` - Enables notes (text field) for writers, labels and artists
* ``FORCE_CASE`` - available options are ``upper`` and ``title`` and ``smart``, converting nearly all strings to UPPER CASE or Title Case or just UPPERCASE fields to Title Case,
  respectively.