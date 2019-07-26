Commercial and Library Releases
===============================

In the previous versions of Django Music Publisher, this was called "Albums and Library CDs", in accordance with CWR 2.x terminology. As these features don't exist in CWR 3.0, they have been renamed.

Under the hood of Django Music Publisher, there is very little difference between Commercial and Library releases, they share the same database table. However, the differences how they are used are significant.

We will first cover simpler Commercial Releases.

Commercial Releases
+++++++++++++++++++

The most typical example of a release used to be a vinyl record album, then a CD. Thesedays...

Django Music Publisher, as open source software, is easily extendable. While currently there is no real use for ``commercial releases`` model with vanilla Django Music Publisher, because this data is not included in CWR registrations,
it may become useful with a custom extension, or with one of the upcoming publicly available extensions.

The ``Commercial release list`` view is quite simple, only three colums, ``Release (album) title``, ``Release (album) label`` and count of tracks with link to ``Recordings``.

The ``Add/change commercial release`` views are also simple, four fields and a list of tracks with optional cut numbers.

Library Releases
++++++++++++++++

Library releases are not only useful, but actually required for production (library) music. To register a work as a library work, in the ``Add/change work`` view, a library release must be selected.

While this may be enough for registrations, a library release can also have tracks (recordings with optional cut numbers). This can be quite useful for integrations with music library software, including the upcoming extension to Django Music Publisher.

The ``Library release list`` view is similar to the one for commercial releases, with three additional colums: ``CD identifier``, ``Library`` and work count with a link to the :doc:`list of works <manual_works_list>` in this library..

The ``Add/change library release`` views are extensions to commercial release views with an additional ``Library`` section.
