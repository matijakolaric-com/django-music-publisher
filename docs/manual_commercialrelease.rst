Commercial (General) Releases
===============================

.. figure:: /images/generalreleases.png
   :width: 100%

The most typical example of a release used to be a vinyl record album, then a CD. It is often referred to as *product*.

Add view
+++++++++++++++++++++++

*Commercial (general)* and *library* releases are actually one model with two different sets of views. 

They share basic 4 fields, as well as inline ``tracks``:

* ``Release title``
* ``Release EAN``
* ``Release label``
* ``Release date``


* ``Tracks``:

  * ``Recording``
  * ``Cut number``
  
.. note::
   **Track** in this software means *recording in a release*.

List view
+++++++++++++++++++++++

``List view`` is quite simple, only three columns, ``Release (album) title``, ``Release (album)
label`` and count of tracks with link to ``Recordings``.
