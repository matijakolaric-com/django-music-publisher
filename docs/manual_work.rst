Musical Works
_____________

Add/Change View
============================================

.. figure:: /images/add_work.png
   :width: 100%

   Add work view, minimal example with default settings

The view for adding and changing works is shown in the image above.
It is the most complex view in Django-Music-Publisher (DMP).
It has several parts, so let us cover them one by one.

General
+++++++

This fieldset contains basic fields.

Field ``work ID``, is set automatically upon first save. This field is extremely
important for data exchange, including registrations and royalty processing.

.. note::
   ``Work ID`` can not be set manually, but it is kept if present in imported data.
   See :doc:`Importing Data <manual_dataimport>` for details.

Work title is entered into ``title`` field.

``ISWC`` (International Standard Musical Work Code) is a unique identifier assigned
to works by a central authority through collecting societies.
It can be edited manually or imported either through
:doc:`data imports <manual_dataimport>` or :doc:`CWR acknowledgements <manual_ackimport>`.

Fields ``title of original work`` and ``version type``, with only the former being
editable, are used for modifications. By filling out ``title of original work``
field, the ``version type`` will be set to ``modification`` and a more
complex set of validation rules will apply.

Library
+++++++

DMP has support for music libraries. If a work is part of
a music library, then a ``Library release`` must be set here.
Details can be found in :doc:`library release <manual_libraryrelease>`.

Writers in Work
+++++++++++++++

This is where you put in the information about writers (composers and lyricists) of the work.
At least one record is required, to add more, click on ``add another writer in work``.

Each column in this table described next.

Writer
------

This is where you select a writer.

This field is conditionally required for controlled writers, and at least one writer in work
must be controlled.

Like many other fields, this field is searchable. You can search by writer's ``last name`` or
``ipi name number``. Click on the desired writer to select them.
To unselect a writer, click the black **x** icon **in the box**.


To add a new writer, click the green plus sign next to it.
To edit the selected writer, click the yellow pencil icon.
To delete the selected writer, click the red **X** icon **outside the box**.
For all three cases,  a pop-up window will appear.

.. figure:: /images/add_writer_popup.png
   :width: 100%

   Add writer pop-up view

The details about the fields in the pop-up window are covered in :doc:`writer <manual_writer>`.

.. note::
    If ``writer`` field is left empty, it means that the writer is unknown.
    This is often used with modifications of traditional musical works.


Role
--------

This is where you select how this writer contributed to the work. This field
is required for controlled writers.

At least one of the writers should be a ``composer`` or a ``composer and lyricist``.

Options for original works are ``composer``, ``lyricist`` and ``composer and lyricist``.

Roles ``arranger``, ``adaptor`` or ``translator`` can only be used in modifications.

For modifications, at least two rows are required, one being (original) ``composer`` or a ``composer and lyricist``,
and one being ``arranger``, ``adaptor`` or ``translator``.

For modifications of traditional works, set the capacity of the unknown writer to ``composer and lyricist`` or
``composer``, depending on whether the original work has lyrics or not.

Manuscript Share
----------------

Django-Music-Publisher (DMP) uses a very simple single-field share model.

Writers create a work and decide how they want to split the shares among themselves. This is referred to as
``manuscript share``.

Each of the writers may choose a publisher and transfer some of their manuscript share to the publisher,
according to their publishing agreement. This does not influence other writers.

In DMP, publishing agreements between all controlled writers and you as the original publisher have
same splits, globally defined in :ref:`settings`.

.. note::
    The sum of relative shares in a work must be 100%.

.. note::
    For a musical work that is a modification of a work in public domain, set the share of
    original writers (``composer``, ``lyricist``, ``composer and lyricist``) to 0.

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

.. note::
    Co-publishing is advanced functionality. You are advised to seek :doc:`professional support <support>`.

Society-assigned agreement number
---------------------------------

In this field, society-assigned agreement numbers for **specific agreements** are entered. For **general agreements**,
they are set when defining the :doc:`writer <manual_writer>`. If both exist and are different, the **specific** one is
used.

.. note::
    This field may be set as required for controlled writers, by setting ``REQUIRE_SAAN`` to ``True``.
    If you used guided deployment, then this value was set automatically to the correct
    value for your society (or societies).


Publisher fee
-------------

This is the fee kept by the publisher when royalties are paid and distributed.

.. note::
    This field is not used in registrations. It is used only for
    :doc:`royalty statement processing <manual_royaltycalculations>`.
    Details are explained in that section. It may also be set as required for
    controlled writers. Same rules apply as for ``society-assigned agreement number``
    field.

Recordings (With Recording Artists and Record Labels)
+++++++++++++++++++++++++++++++++++++++++++++++++++++

This is where the details about a recording based on this musical works are
added. Athough there is a separate set of views for
:doc:`recordings <manual_recordings>`, fields in this section are explained
only here.

.. note::
    For this version of DMP, it is recommended to edit recordings here.

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

This is where the work registration acknowledgements are recorded.

.. note::
    In the default configuration, only superusers can modify this section, as it is automatically filled out from :doc:`uploaded acknowledgement files <manual_ackimport>`.

Saving and Deleting
+++++++++++++++++++

At the bottom, there is a delete button and three save buttons. Delete is obvious. The save buttons do following:

* ``Save and add another`` (when adding new work) saves the work and then opens a new, empty form for the next one.
* ``Save as new`` (when editing existing work) saves this data as a new work (with a different work ID)
* ``Save and continue editing`` saves the work and then opens the same work for further editing.
* ``SAVE`` saves the work and returns to the ``list view``, covered next.

The combination is extremely powerful, especially when the changes between works is small, as is often the case for production music.
One enters the first work, using suffixes as much as possible, presses on ``save and continue editing``.
If save was successful, then the data can be changed for the next work, and then one presses on ``save as new``, and this new work is saved.
The process can be repeated for all the works in the set.

List View
========================

.. figure:: /images/work_list.png
   :width: 100%

   Work list view

The ``work list`` view, just as all other list views, has a ``search field``, an ``action bar``, a table with works and, once there are over 100 works in the database, pagination, all on the left side. On the right side, there is the ``add musical work`` button, which takes you to the appropriate view, and the set of ``filters``.

Filters change, based on the number of options. For four options or less, they are simple links, and for more, it turns into a pull-down menu.
``Last edited`` filter allows find all works that have been changed recently. This applies to
all objects that participate in work registrations, e.g. writers.

Search works on titles, writer's last names, ISWCs, ISRCs (in related recordings) and work IDs (numeric part).

Data table can be sorted by almost any column, or combination of the columns, and counts are also links to :doc:`recording <manual_recordings>` and :doc:`CWR export <manual_cwr>` ``list`` views..

Exporting JSON
++++++++++++++++++++++++++

.. figure:: /images/work_list_action.png
   :width: 100%

   Exporting musical works in JSON format.

Select several (or all) works in the ``musical work list`` view, select the ``Export selected works (JSON)`` action and
press on ``Go``. A JSON file will be downloaded, containing **all** the information about your works.

If you ever choose to stop using Django-Music-Publisher and move on, there is no lock-in. While these JSON formats might
be confusing, there are free on-line tools that will convert JSON to just about any other format you need.

.. _exporting_csv:

Exporting CSV
++++++++++++++++++++++++++

Select several (or all) works in the ``musical work list`` view, select the ``Export selected works (CSV)`` action and
press on ``Go``. A CSV file will be downloaded, containing **only basic** information about your works.

It contains no data about the controlling publisher (you) and recordings, including recording
artists, labels, tracks and releases.

This CSV format is the same as the one used for :doc:`Importing data <manual_dataimport>`, with
one additional column: ``Work ID``.

CWR Exporting Wizard
++++++++++++++++++++

Currently, the only other available action is to ``create CWR from selected works``. Once you run it, you will be taken
to ``add CWR export`` view, described :doc:`here <manual_cwr>`.
