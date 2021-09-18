Integration (Rest API)
====================================

DMP is very good at data management and validation, but not made for public
presentation of this data. Still, it makes no sense to enter the same data
over and over again. Now you don't have to.

DMP has provides several browsable read-only API endpoints 
for integration with other software, most notably user's website.

The address of the API root, relative to the home page, is: ``api/v1/``.


Featured Releases and Artists
------------------------------------------

Releases, artists, writers and labels now feature fields ``image`` and 
``description``, to be used for public content presentation. Recordings
feature ``audio file`` field for the same reason.

There are endpoints for getting lists of all artists and releases 
(both commercial and library), with data in either ``image`` or ``description`` 
field, as well as details about an artist or a release.
Details contain data about recordings (including audio files if they exist),
record labels, underlying musical works and writers.

* ``/api/v1/artists/``
* ``/api/v1/releases/``

These endpoints are not publicly available, they are protected by ``Basic HTTP 
Authentication``. It is recommended to create a dedicated user, has to be active, 
and has to have permission ``Can view Performing Artist`` and/or ``Can view 
Release``.

One use example is to provide list of artists and/or releases on your website
through a plugin. You do it once, and then your website will always be up-to-date,
as long as you enter the data in DMP.

.. warning::

   THIS FEATURE IS BEING DEVELOPED, IT IS NOT READY FOR PRODUCTION!


Shareable Playlists
--------------------------------------------

A sharable playlist can be accessed through a normal HTML
interface, or through a REST API endpoint. Both URLs can be found
in the ``change view``. 

There is currently no way to get a list of all secret playlist. 

Backup Metadata
--------------------------------------------

* ``/api/v1/backup_metadata/``

This endpoint can be used to get all the metadata about all
works and releases. However, public data (descriptions, images 
and audio files) are not included.

It is available only to a ``superuser``, because it's purpose is to provide 
one-time backup if you choose to move to a different system.

.. note::

   If you are moving from DMP to 
   `That Green Thing <https://thatgreenthing.eu/>`_,
   the migration is fully automated.
