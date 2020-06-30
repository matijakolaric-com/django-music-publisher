Recordings
==========

.. note::
    Django-Music-**Publisher** is primarily software for music publishers. It can store metadata about recordings, but not audio files.

Add/Change view
-------------------------------

There are three ways to add or edit recordings in DMP, in order of importance:

* in ``add/change view`` of :doc:`musical works <manual_work>`, in section ``Recordings``
* in ``add/change view`` of releases (:doc:`commercial <manual_commercialrelease>` and :doc:`library <manual_libraryrelease>`), through pop-ups in ``tracks``
* in ``add/change view`` of recordings (described here)

The first exists because that is the most natural way for publishers to add them. The second exists because recordings are released on releases (albums, products) as ``tracks``. The last, for consistent user experience.

.. figure:: /images/add_recording.png
   :width: 100%

   Add recording

Compared to the ``Recordings`` section in ``add work`` view, there is only one additional field at the top, 
where the work can be chosen or added through a popup.

.. note::
    DMP only supports recordings based on a single musical works. The link between a recording and the underlying musical work is required.

``Recording title`` should only be used if the title is different than the work title. ``Version title`` should only be 
used if different from the ``recording title``. The use of suffixes is explained in :doc:`works <manual_work>`, 
section ``Alternative titles``.
section.

``ISRC`` is International Standard Recording Code. 

``Record label``, ``recording artist``,
``duration`` and ``release date`` are obvious. ``Duration`` can be entered in seconds or in
``HH:MM:SS`` format. It will always be shown in the latter format.


List view
------------------------------------------------

.. figure:: /images/recordings.png
   :width: 100%

   Recording list view

``Recording list`` view provides a nice overview, with search and filter capabilities and links for :doc:`work <manual_work>`, :doc:`recording artist <manual_artist>` and :doc:`record label <manual_label>`.

