Library Releases
===============================

.. figure:: /images/libraryreleases.png
   :width: 100%


Add view
+++++++++++++++++++++++

:doc:`Commercial (general) <manual_commercialrelease>` and *library* releases are actually one model with two different sets of views.
The only difference is that *library* releases have two additional fields both required:

* ``Library``
* ``CD identifier`` - a CWR field name for *release code*


List view
+++++++++++++++++++++++

``List view`` has 6 columns, 3 more than *commercial* releases. Two of them are for the two aforementioned field. The last one is a counter and a link to :doc:`works <manual_work>`. This field will list works that have ``library release`` field set to this library release.
