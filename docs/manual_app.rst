Music Publishing App
====================

.. figure:: /images/home.png
   :width: 100%

   Home view for staff users

``Music Publisher`` has several top-level models, and each model has several views.

Views
+++++

Every model has at least 4 views:

* ``List`` - view listing objects, includes search, filtering and batch actions
* ``Add`` - view for adding new objects
* ``Change`` - view for changing an object, includes delete button
* ``History`` - view where changes to a work are shown, accessible from ``change`` view

``Add`` and ``change`` are usually very similar. They often contain forms for editing related models. E.g. in ``add musical work``, one can also add alternate titles.

Models
++++++

Each model is a representation of an aspect of something from the real world. It has attributes that describe this aspect, and performs actions representing real world actions.

We are just briefly going to describe the top level models here, each will be then described in detail in a separate section.

Works
-----

`Work` model represents musical works and it is the workhorse model in Django Music Publisher. And it's ``add`` and ``change`` views are the most complex ones, with data on related recordings, writers, performing artists, alternate titles etc.
It also has several batch actions, e.g. data export.

Commercial and Library Releases
-------------------------------

Release is, generally speaking, a product containing one or more recordings, e.g. records and albums. The importance of the physical forms is diminishing, but they are still important enough to be part of a music publishing software, especially for music libraries.

Labels and Libraries
--------------------

Two very simple models, but their importance will grow with the upcoming extensions to Django Music Publisher.

Performing Artists
------------------

One of the simpler models, beside the data about the artist, it's views also show recordings the artists made and works they perform.

Recordings
----------

The views for recordings are, strictly speaking, not needed, as this data is accessible from other views: works and releases. It is recommended not to use this model for editing. On the other hand, it's ``list`` view is handy for searching and filtering.

Writers
-------

Composers and lyricists are usually called "writers", the term dating back to days when sheet music was the only way of music distribution. This model is very important, though simple,
as it holds not only data about the writers, but also about their affiliations, agreements, etc.

CWR Exports
-----------

Common Works Registration is a file format for batch registration of musical works in collecting societies (aka PROs/MROs). This model is used for creating these files.

CWR ACK Imports
---------------

Once a collecting society processes a CWR file, they send an acknowledgement file (or several files). This model is used for data import from these files.
