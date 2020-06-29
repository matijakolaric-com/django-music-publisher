Recordings
==========

.. note::
    Django-Music-**Publisher** is primarily software for music publishers. It can store metadata about recordings, but not audio files.

Add/Change view
-------------------------------

.. note::
    DMP only supports recordings based on a single musical works. The link between a recording and the underlying musical work is required.

There are actually three ways to add or edit recordings in DMP, in order of importance:

* in ``add/change view`` of :doc:`musical works <manual_work>`, in section ``Recordings``
* in ``add/change view`` of releases (:doc:`commercial <manual_commercialrelease>` and :doc:`library <manual_libraryrelease>`), through pop-ups in ``tracks``
* in ``add/change view`` of recordings (described here)

The first exists because that is the most natural way for publishers to add them. The second exists because recordings are released on releases (albums, products) as ``tracks``. The last, for consistent user experience.


Compared to the ``Recordings`` section in ``Works``, there is only one additional field at the top, where the work can be chosen or added through a popup,
and a ``Tracks`` section at the bottom, connecting a recording with a :doc:`release <manual_releases>`.

Note that a ``Work`` popup holds only a subset of fields compared to the normal view. The data that is not visible will **not** be lost when saving through popup.

List view
------------------------------------------------

.. figure:: /images/recordings.png
   :width: 100%

   Recording list view, note the use of search and filters

``Recording list`` view provides a nice overview, with it's search and filter capabilities and links for :doc:`work <manual_work>`, :doc:`recording artist <manual_artist>` and :doc:`record label <manual_labels>`.


Recording title
---------------

There are three fields in this row. ``Recording title`` is where one enters the title of the recording. If ``recording title suffix`` is checked, then the former field is used as a suffix to the ``work title``. This is a huge benefit in production music, where there are multiple recordings per work, usually with same suffixes, e.g. "drums", "bed", etc. The result is then shown in the ``complete recording title`` field.

Version title
-------------

Same is valid for the ``version title``, except that the suffix is added to the ``recording title``.

Other fields
------------

``ISRC`` is a unique identifier, issued by record labels. ``Recording artist``, ``record label``, ``duration`` and ``release date`` are quite obvious.

Note that after a successful save, there is a ``change`` link in the recording header.

