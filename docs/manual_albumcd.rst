Albums and Libraries
====================

So far, in this manual, we have created basic musical works and CWR registrations, without any data on recordings, albums and/or libraries.

As it was mentioned in the section on adding and changing works, it is possible to add this information through ``Add Work view``. That is the preferred way if information is available from the start of the input process. However, sometimes we want to register works before we have data on recordings. While opening every work and adding the data is definitely an option, there is a faster way.

Press ``Add`` next to ``Albums and Library CDs``. The following interface appears:

.. figure:: /images/albumcd_add.png
   :width: 100%

   Album and/or Library CD Add view

This view has three sections: library, album and tracks. Either library data or album data or both must be entered.

Production music library
++++++++++++++++++++++++

Library refers to production music library. Please note that if ``LIBRARY`` is not present in settings, the field ``CD Identifier`` will not be present either. Django Music Publisher does not support multiple libraries. It also does not support other origins, such as film, theatre, television etc.

If you wish to mark a work as a library work, you must enter ``CD Indentifier``, the CWR documentation recommends to put in ``INTERNET`` if you do not care about identifiers, though some societies use this field for identification and royalty distribution. Please contact your society for details.

If you leave this field empty, the work will not be marked as library work.

Albums
++++++

The second part of this view holds information about the album (or any other release). You may also use it as a place-holder. ``Album name`` is required, other data is optional.

Tracks
++++++

In the last part, you can enter tracks. This is the same data that can be entered through ``Add/Change Work view``, in the part ``First recording``.

Please note that Django Music Publisher is limited to first recordings/releases, so it is not possible to add one work to more than one album. You should NOT try to go around this limitation by creating duplicate works, it will create issues that will be hard to resolve. If you really need that feature, then Django Music Publisher is not the right solution for you.

The field ``release date`` is present both in album data and in track data. If both are entered, then the one from track data is used. There is no need to enter the same date in both locations, though it will not break anything if you do.

.. figure:: /images/tracks_added.png
   :width: 100%

   Example with added tracks. Please note that the first track has an earlier release date.

Registering revised works
+++++++++++++++++++++++++

If you have already registered, you probably want to create a new, revised registration. The way we do this, is to go back to the ``Works list view``. It will now show new information for the works we have added to the Album and/or Library.

.. figure:: /images/albumcd_effects.png
   :width: 100%

   The first three works now have Album/Library CD data present. You may open any of them to see how these changes affected data in them.

Select these works, and choose to create a CWR export, then select ``revision`` for CWR 2.1, for CWR 3.0, there is no special selection, as societies are supposed to know what to do, and press ``Save``. You may choose to compare the two files.

.. figure:: /images/cwr_rev.png
   :width: 100%

   The differences are marked, there are additional records and the first record for each transaction (work registration) starts with REV.