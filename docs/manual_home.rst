Basics
========================

This section explains the very basics, logging in, home view and general
overview of model views.

Login
+++++++++++++++

.. figure:: /images/dmp_login.png
   :width: 100%

   Default log-in view

The first screen that appears is the log-in screen. Please log in with your credentials.

Home view
+++++++++++++

.. figure:: /images/dmp_home.png
   :width: 100%

   Home view for superusers

The ``home view`` will show up after a successfully login. It changes, based on
user permissions. In this example, it is the view superusers see -- everything.

In the header, the left part shows the name of the (main) publisher and the link to the maintainer's website.
The right shows links to this user manual, for changing the password and logging out. This header is present in all views.

We have two columns, the left one shows sections of modules, with links to change and add views.
The right column shows up to 10 latest actions of the current user.

Model Views
+++++++++++++++

Every model has at least 4 views:

* ``List`` - view listing objects, includes search, filtering and batch actions
* ``Add`` - view for adding new objects
* ``Change`` - view for changing an object, includes delete button
* ``History`` - view where changes to a work are shown, accessible from ``change`` view

``Add`` and ``change`` are usually very similar. They often contain forms for editing related models.
E.g. in ``add musical work``, one can also add alternate titles, recordings, etc.
