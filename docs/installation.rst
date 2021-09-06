Installation and Upgrading
****************************************

Installation on  Heroku or Digital Ocean
++++++++++++++++++++++++++++++++++++++++++++++++++++

`This wizard <https://dmp.matijakolaric.com/install/>`_ will help you in deploying
DMP to Heroku or Digital Ocean.

.. figure:: /images/pre_wizard.png
   :width: 100%

Fully automated deployment to Heroku
======================================================

This is the simplest option, and free for publishers with up to several hundreds 
of musical works, if you don't need file uploads and related features (currently
only sharable playlists).

Free tier, sufficient for publishers with hundreds of works has two limitations that 
can both be removed for $16 per month.

* Your instance goes to sleep after a while. When you access it, it takes 30 seconds
  to spin up.
* Your database is limited to 10.000 rows, which is enough for publishers with several 
  hundred works

Valid e-mail address is required for registration, but no payment information.

The whole process takes under 5 minutes, and other than entering the data
about the publisher and initial password, it is all menus and next-next-next.

Assisted deployment to Digital Ocean
======================================================

Digital Ocean provides no free tier. For $17 per month, you can have your DMP 
instance running all the time, and this includes file storage. If you use 
``this affiliate link``, you will get $100 of free credits, so you get almost 
6 months for free.

The deployment process is not fully automated, and includes reading the instructions,
copy-pasting of data, etc. It takes between 15 and 30 minutes.

Upgrading
+++++++++++++++++++++++++++++++++++++++

Heroku
==========================================

While installation to Heroku is really simple, updating requires some technical knowledge. The simplest way to update is to install `Heroku CLI (command line interface) <https://devcenter.heroku.com/articles/heroku-cli>`_. It can be installed on Windows, Mac and Linux.

Then you log in, clone the repository, enter the folder, add a new remote and push:

.. code-block:: bash

   $ heroku login
   $ git clone https://github.com/matijakolaric-com/django-music-publisher.git
   $ cd django-music-publisher/
   django-music-publisher$ heroku git:remote --app yourapp 
   django-music-publisher$ git push heroku master
   
If you are upgrading from a version older than 20.7, you may need to delete an old buildpack, which can be found in Heroku dashboard in the ``Settings`` tab.

Digital Ocean
==========================================

If you followed the deployment instructions, upgrades are fully automatic.

Manual installation
++++++++++++++++++++++++++++++++++++++++++++++++++++++

DMP - Django-Music-Publisher is based on Django, which can be installed on Windows,
Mac and Linux PCs and servers. For more information, consult the official
`Deploying Django <https://docs.djangoproject.com/en/3.0/howto/deployment/>`_ documentation.

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

For the list of codes, please have a look at societies.csv file in the music_publisher
folder of the code repository.

Agreement-related settings
-----------------------------------

* ``PUBLISHING_AGREEMENT_PUBLISHER_PR`` - Performance share transferred to the publisher, default is '0.5' (50%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_MR`` - Mechanical share transferred to the publisher, default is '1.0' (100%)
* ``PUBLISHING_AGREEMENT_PUBLISHER_SR`` - Synchronization share transferred to the publisher, default is '1.0' (100%)

Case change
------------------------------------

* ``OPTION_FORCE_CASE`` - available options are ``upper``, ``title`` and ``smart``, 
  converting nearly all strings to UPPER CASE or Title Case or just UPPERCASE fields 
  to Title Case, respectively.