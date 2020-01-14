Musical Works: Adding, Changing and Deleting
============================================

.. figure:: /images/add_work.png
   :width: 100%

   Add work view, minimal example with default settings

The view for adding and changing works is shown in the image above. It is the most complex view in Django-Music-Publisher. It has several parts, so let us cover them one by one.

General
+++++++

This part contains basic fields. Field ``work ID``, which is set automatically upon first save. This field is extremely important for registrations. The proper explanation is beyond the scope of this manual.

``title`` should be obvious. Please note that the label ``title`` is bold, representing that this field is required. ``ISWC`` is a unique identifier assigned to works by collecting societies.

Fields ``original title`` and ``version type``, with only the former being editable, are used for modifications. By filling out ``original title`` field, the ``version type`` will be set to ``modification`` and a more complex set of validation rules will apply.

Please note that the difference between modifications of works in public domain and those where copyright still exists is set through ``writers in work`` section.

Library
+++++++

Django-Music-Publisher has good support for music libraries. If a work is part of a :doc:`library <manual_labels_libraries>`, then a :doc:`library release <manual_releases>` must be set here.

Writers in Work
+++++++++++++++

This is where you put in the information about :doc:`writers <manual_writers>` (composers and lyricists) who created this musical work. At least one is required, to add more, click on ``add another writer in work``.

Each column is described next.

Writer
------

This is where you select a :doc:`writer <manual_writers>`. The field is conditionally required for a controlled writer, and at least one writer must be controlled.

To add a writer, press on the green plus ``+`` sign next to it. A pop-up window will appear. Fill out ``first name``, ``last name``, ``IPI name #`` and ``performance rights society``, and press on ``save``. The newly added writer will appear in this field.

There is another way to add writers, which will be covered in the :doc:`writers <manual_writers>` section.

If left empty, it means that the writer is unknown. This is often used with modifications of traditional musical works.


.. figure:: /images/popup_add_writer.png
   :width: 100%

   Add writer pop-up view

Capacity
--------

This where you select how this writer contributed to the work. This field is required for controlled writers. Please note that at least one of the writers should be a ``composer`` or a ``composer and lyricist``.

The options are ``composer``, ``lyricist`` and ``composer and lyricist`` for original works. ``Arranger``, ``adaptor`` or ``translator`` can only be used in modifications. For them, at least two rows are required, one being (original) ``composer`` or a ``composer and lyricist``, and one being ``arranger``, ``adaptor`` or ``translator``.

For modifications of traditional works, set the capacity of the unknown writer to ``composer and lyricist``.

Manuscript Share
----------------

Django-Music-Publisher uses a very simple single-field share model. The principle is very simple.
Writers create a work and decide how they want to split the shares among themselves. This is referred to as
``manuscript share``. (The term comes form CWR 3.0 specification.) Then each of the writers may choose a publisher
and transfer some of their manuscript share to the publisher, according to their publishing agreement.
This does not influence other writers.

In Django-Music-Publisher, publishing agreements between all controlled writers and you as the original publisher have
the same splits, globally defined in settings.

The sum of relative shares for each work must be 100%.

For a musical work that is a modification of a public domain one, set the share of original writers
(``composer``, ``lyricist``, ``composer and lyricist``) to 0.

.. figure:: /images/works_pd.png
   :width: 100%

   Writers in work for a work that is a modification of a work in public domain

Controlled
----------

This is where you select whether you control the writer or not. Select it for at least one ``writer in work`` row.

A writer can be entered in two rows, once as controlled, once as not. This allows for co-publishing deals. If there is more than one other publisher per writer, add their shares to a single row.

.. figure:: /images/works_copub.png
   :width: 100%

   Writers in work for a co-published work

Society-assigned agreement number
---------------------------------

In this field, society-assigned agreement numbers for **specific agreements** are entered. For **general agreements**,
they are set when defining the :doc:`writer <manual_writers>`. If both exist and are different, the **specific** one is
used.

This field may be set as required for controlled writers.


Publisher fee
-------------

This is the fee kept by the publisher when royalties are paid and distributed. **This field is not used in
registrations.** It is used only for royalty statement processing. Most small publishers don't use it.

It may also be set as required for controlled writers. Same rules apply as for ``society-assigned agreement number``
field.

Recordings (With Recording Artists and Record Labels)
+++++++++++++++++++++++++++++++++++++++++++++++++++++

Since version 19.7, Django-Music-Publisher has full CWR 3.0 compatibility, except that id does not allow for recordings based on multiple works (medleys). This means that data about recordings is now quite complex and detailed.

Please note that, although there is a separate set of views for :doc:`recordings <manual_recordings>`, it is recommended to edit them here.

.. figure:: /images/works_recordings.png
   :width: 100%

   Add work view, recordings section, note the use of recording and version title suffix checkboxes

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


Alternative Titles
++++++++++++++++++

Alternative titles section is for alternative titles. There is no need to enter the recording or version titles from recordings section. The suffixes work the same way as for ``recording titles``.

Artists Performing Works
++++++++++++++++++++++++

Here you list the artists who are performing the work, there is no need to repeat the artists set as ``recording artist`` in the ``recordings`` section.

Registration Acknowledgements
+++++++++++++++++++++++++++++++++++

This is where the work registration acknowledgements are recorded. Please note that only superusers (in the default configuration) can modify this section, as it is automatically filled out from :doc:`uploaded acknowledgement files <manual_ack>`.

Saving and Deleting
+++++++++++++++++++

At the bottom, there is a delete button and three save buttons. Delete is obvious. The save buttons do following:

* ``Save and add another`` (when adding new work) saves the work and then opens a new, empty form for the next one.
* ``Save as new`` (when editing existing work) saves this data as a new work (with a different work ID)
* ``Save and continue editing`` saves the work and then opens the same work for further editing.
* ``SAVE`` saves the work and returns to the :doc:`work list view <manual_works_list>`, covered next.

The combination is extremely powerful, especially when the changes between works is small, as is often the case for production music.
One enters the first work, using suffixes as much as possible, presses on ``save and continue editing``.
If save was successful, then the data can be changed for the next work, and then one presses on ``save as new``, and this new work is saved.
The process can be repeated for all the works in the set.

