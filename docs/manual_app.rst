Music Publisher App
====================

.. figure:: /images/home.png
   :width: 100%

   Home view for staff users

``Music Publisher`` has several top-level models, and each model has several views. This is what members of the
``Publishing Staff`` group see when they log in. Note that there is no data in the right column when a new user logs in.

Views
+++++

Every model has at least 4 views:

* ``List`` - view listing objects, includes search, filtering and batch actions
* ``Add`` - view for adding new objects
* ``Change`` - view for changing an object, includes delete button
* ``History`` - view where changes to a work are shown, accessible from ``change`` view

``Add`` and ``change`` are usually very similar. They often contain forms for editing related models. E.g. in ``add musical work``, one can also add alternate titles.

Models Groups
+++++++++++++

Each model is a representation of an aspect of something from the real world. It has attributes that describe this aspect, and performs actions representing real world actions.

We are just briefly going to describe the top-level models here, each will be then described in detail in a separate section. Models are
separated in several logical groups.

Group Musical Works
___________________

.. toctree::
   :maxdepth: 1

   manual_works
   manual_writers
   manual_cwr
   manual_ack


Group Recordings
________________

.. toctree::
   :maxdepth: 1

   manual_recordings
   manual_artists
   manual_labels

Group Releases
________________

.. toctree::
   :maxdepth: 1

   manual_releases
   manual_libraries

Group Other
________________

.. toctree::
   :maxdepth: 1

   manual_dataimport

