Musical Works
_____________

This part explains views for Musical Work model specifically, but
much of it applies to views of other models as well.

.. contents::
   :backlinks: none
   :local:
   :depth: 2


Add/Change View
============================================

.. figure:: /images/add_work.png
   :width: 100%

   Add work view

The view for adding and changing works is shown in this screenshot.
It is the most complex view in Django-Music-Publisher (DMP).
It has several parts, which will be covered one by one.

General
+++++++

This fieldset contains basic fields.

Field ``work ID`` is not editable in this view.

.. note::
   ``Work ID`` is set by DMP, but it can also be imported.
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

Each column in this table is described next.

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
    This field is required for controlled writers in some collecting societies,
    while not used in most.
    You can make it a required field by setting ``REQUIRE_SAAN`` to ``True``.
    With guided deployment, this value is automatically set to the correct
    value for your collecting society (or societies).


Publisher fee
-------------

This is the fee kept by the publisher when royalties are paid and distributed.

.. note::
    This field is not used in registrations. It is used only for
    :doc:`royalty statement processing <manual_royaltycalculations>`.
    Details are explained in that section.

.. note::
    This field may be set as required for controlled writers, by setting ``REQUIRE_PUBLISHER_FEE`` to ``True``.
    

Recordings (With Recording Artists and Record Labels)
+++++++++++++++++++++++++++++++++++++++++++++++++++++

This is where the details about a recording based on this musical works are
added. There is a separate set of views for
:doc:`recordings <manual_recording>`, fields are explained there.


Alternative Titles
++++++++++++++++++

Alternative titles section is for alternative titles. There is no need
to enter the recording or version titles already entered in the recordings section.

Field ``alternative title`` is where you enter the title, or it's suffix,
based on the field ``suffix``. If the latter is checked, then the suffix
will be appended to the work ``title``. The actual alternative title is always
shown in the read-only field ``complete alt title``.

.. note::
    Title suffixes are advanced functionality.
    You are advised to seek :doc:`professional support <support>` before
    using them.


Artists Performing Works
++++++++++++++++++++++++

Here you list the artists who are performing the work, there is no need to
repeat the artists already set as ``recording artists`` in the ``recordings`` section.

The field ``artist`` behaves similarly to the field `Writer`_.

Registration Acknowledgements
+++++++++++++++++++++++++++++++++++

This is where the work registration acknowledgements are recorded.

.. note::
    In the default configuration, only superusers can modify this section, as it is automatically filled out from :doc:`uploaded acknowledgement files <manual_ackimport>`.

Saving and Deleting
+++++++++++++++++++

At the bottom, there is a delete button and three save buttons.

``Delete`` button starts the deletion of the work and all related objects.
A confirmation screen shows all objects being deleted.

.. note::
    Deleting a work is not always allowed, regardless of user permissions. E.g.
    if a :doc:`CWR acknowledgement <manual_ackimport>` for this work exists.
    If you are sure you want to delete a work, a superuser must delete
    such linked objects first. You are advised to seek
    :doc:`professional support <support>` before doing that.

The save buttons do following:

* ``Save and add another`` (when adding new work) saves the work and then opens a new, empty form for the next one.
* ``Save as new`` (when editing existing work) saves this data as a new work
  (with a different work ID). Note that you must change all unique fields as well, e.g.
  ISWC.
* ``Save and continue editing`` saves the work and then opens the same work for further editing.
* ``SAVE`` saves the work and returns to the ``list view``, covered next.

The combination is extremely powerful, especially when the changes between works is small.

Enter the first work, using suffixes as much as possible, click on ``save and continue editing``.
If successful, then data make the changes for the next work, and click on ``save as new``,
and this new work is saved.

List View
========================

.. figure:: /images/work_list.png
   :width: 100%

   Work list view

The ``work list`` view, just as all other list views, has a ``search field``,
an ``action bar``, a table with works and, once there are over 100 works,
pagination, all on the left side.

Search looks for titles, writer's last names, ISWCs, ISRCs
(in related recordings) and work IDs.

Data table can be sorted by almost any column or combination of the columns.

Counts of related objects are also links to
:doc:`recording <manual_recording>` and
:doc:`CWR export <manual_cwrexport>` ``list``
views, filtered for this work.

On the right side, there is the ``add musical work`` button,
which takes you to the appropriate view, and the set of ``filters``.

Filters change, based on the number of options. For four options or less,
they are simple links, and for more, they turn into a pull-down menus.

``Has ISWC`` will show only works with ISWCs or only works without them.

``Has recordings`` will show only works with recordings or only works without them.

``Library`` will list only works in a particular :doc:`library <manual_library>`.

``Library Release`` will list only works in a particular :doc:`library release <manual_libraryrelease>`.

``Writers`` will list only works by a particular :doc:`writer <manual_writer>`.

``Last edited`` filter allows find all works that have been changed recently,
including related objects, e.g. writers.

Filters and search can be combined. Only works fulfilling all the criteria will be shown.

Exporting JSON
++++++++++++++++++++++++++

.. figure:: /images/work_list_action.png
   :width: 100%

   Exporting musical works in JSON format.

Select several (or all) works in the ``musical work list`` view, select the ``Export selected works (JSON)`` action and
click ``Go``. A JSON file will be downloaded, containing **all** the information about your works.

.. _exporting_csv:

Exporting CSV
++++++++++++++++++++++++++

Select several (or all) works in the ``musical work list`` view, select the ``Export selected works (CSV)`` action and
click ``Go``. A CSV file will be downloaded, containing **only basic** information about your works.

It contains no data about the controlling publisher (you) and recordings, including recording
artists, labels, tracks and releases.

This CSV format is the same as the one used for :doc:`Importing data <manual_dataimport>`.

CWR Exporting Wizard
++++++++++++++++++++

Currently, the only other available action is to ``create CWR from selected works``.
Once you run it, you will be taken to :doc:`CWR Export <manual_dataimport>` view
with your work selection.

.. note::
    ``Create CWR from selected works`` action is only visible if
    ``PUBLISHER_CODE`` is defined in :ref:`settings`.
