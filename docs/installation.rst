Installation and Upgrading
****************************************

Installation
++++++++++++++++++++++++++++++++++++++++++++++++++++

`This wizard <https://dmp.matijakolaric.com/install/>`_ will help you in deploying
DMP.

.. figure:: /images/pre_wizard.png
   :width: 100%

In the last step, you will be asked where you want to deploy it. Below are the options.

Heroku
======================================================

Deployment
--------------------

This is the simplest option, and free for publishers with up to several hundreds 
of musical works. File storage and related features are not available out of the box,
and file storage is very expensive if acquired through Heroku Marketplace.

Free tier has two limitations that can both be removed for $16 per month.

* Your instance goes to sleep after a while. When you access it, it takes 20-30 seconds
  to spin up.
* Your database is limited to 10.000 rows.

Valid e-mail address is required for registration, but no payment information.

The whole process takes under 5 minutes, and other than entering the data
about the publisher and initial password, it is all menus and next-next-next when using the
`wizard <https://dmp.matijakolaric.com/install/>`_.

Upgrading
-------------------

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
======================================================

Deployment
--------------------------------------

Digital Ocean provides no free tier. For $17 per month, you can have your DMP 
instance running all the time, and this includes file storage. You will be
asked for email address and payment information (credit card or PayPal).

The deployment process can not be fully automated. It requires a bit of copy-pasting and selecting the options
yourself. It can still be achieved in 5 - 10 minutes by most people if you follow these instructions closely.

First, complete the `wizard <https://dmp.matijakolaric.com/install/>`_. It ends with this screen.
Don't close it until your installation is finished.

.. figure:: /images/installation_do_1.png
   :width: 100%

Click on the ``Deploy to DigitalOcean`` button. This will take you to Digital Ocean
in a new tab. Once you have completed the registration, their wizard starts.

Do not change values already set, unless you know exactly what you are doing.
All you have to do is add values of variables explained here and those from the 
first wizard.

* ''DJANGO_SUPERUSER_USERNAME'' is the username of your first user.
* ''DJANGO_SUPERUSER_PASSWORD'' is the initial password of your first user, you can and should change it in the app later.
* Variables starting with ''S3'' are used for file storage, setting this up is explained later in this document.

Copy-paste the of environment variables rest from the first wizard. Feel free to change ''SECRET_KEY'' to something else.

In the second step, you select the size of your instance. The smallest ``Basic`` option should be enough for any small
publisher. Then just finish the wizard.

File Storage
----------------------

Support for file uploads was only added in 2022, and is not required for registrations
of musical works or royalty processing. Currently, it is only used for secret sharable playlists
and in presenting this data elsewhere (e.g. your website) using REST API.

.. figure:: /images/installation_do_f1.png
   :width: 100%

Digital Ocean calls their S3 storage "Spaces", where one space is really an S3 bucket.
The defaults are fine, just give it a name, and this name goes into 'S3_BUCKET' variable.



Upgrading
----------------------

To be explained


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

S3 storage
------------------------------------

Recommended S3 provider is Digital Ocean, it is simpler to set up and more affordable 
than AWS. They call S3 *Spaces*. 

For Digital Ocean, you need to set up only four settings.

* ``S3_REGION`` (alias for ``AWS_S3_REGION_NAME``) and ``S3_BUCKET`` 
  (alias for ``AWS_STORAGE_BUCKET_NAME``), you get them when you set up your *Spaces*,
  and

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
  to Title Case, respectively.

* ``OPTION_FILES`` - enables support for file uploads (audio files and images), using 
  local file storage
