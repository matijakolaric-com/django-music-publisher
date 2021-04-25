Importing Data
==============================

.. note:: Default *Publishing Staff* permission group does not include data imports because importing data is not everyday routine.

Musical works metadata can be imported from CSV files.

.. warning:: There is no way to undo a successful import other than by restoring your database from a backup. If you don't know how to back up and restore your database, do not import data!


What is being imported?
_______________________

The import process will *add* works, including alternative titles, writers, recordings (partial), performing artists, 
libraries, library releases and society work references.

No data is ever *modified*, with only one exception. A general agreement for an existing writer may be
*set* and a society-assigned agreement number may be *added*.

Why are errors reported?
_________________________

If data in the file is incomplete or conflicting with data in the database (or other data in the
same file), an error will be thrown. Not all errors shown in a user-friendly way.

.. note:: When an error is thrown, no changes to the database occur.

Work IDs
________

The template contains ``Work ID`` column. If you never assigned IDs to works, leave this blank.
The system will generate work IDs. Note that this is *not* the ID given by your society or any third party.

On the other hand, work IDs must be maintained when moving from one software to another. Failing to do so
may overwrite your existing registrations at collecting societies or create duplicates.

.. warning:: Not assigning work IDs when required will lead to double registrations and other issues.

.. warning:: Assigning wrong work IDs will lead to registrations cancelling each other.

How to import?
------------------------------

Obtaining and extending the template
__________________________________________________

Download the CSV template from the `Add Data Import` view.
You can edit it in Excel or another spreadsheet tool. 

It contains 6 columns for alternative titles, as well as
6 column sets for writers, recordings and artists.

For another writer column set, add all of:
``Writer 7 Last``, ``Writer 7 First``, ``Writer 7 IPI``, ``Writer 7 PRO``, ``Writer 7 Role``,
``Writer 7 Manuscript Share``, ``Writer 7 Controlled``, ``Writer 7 SAAN``. 

You can add as many writer-, recording-, artist- and alternative-title-sets as you require. Just keep incrementing
the counter.

Note that this file has a subset of columns described in :ref:`exporting_csv`.

Filling out the template
______________________________

Fill out the template. Make sure to save as CSV.

Values in ``Writer PRO``, ``Writer Role`` and ``Writer Controlled`` columns must start with correct codes.

``Writer PRO`` must start with society code without the leading zero.
``10``, ``10 ASCAP``, ``10 - ASCAP`` or ``10 - BMI`` will all resolve as ASCAP. ``ASCAP`` without the code
will throw an error.

``Writer Role`` must start with one of ``C``, ``A``, ``CA``, ``AR``, ``TR``  or ``AD``, e.g. ``C - Composer``.

``Writer Controlled`` should be set to ``No``, ``Yes`` or ``General`` (see :doc:`Writer <manual_writer>` for details).

Data upload
______________________________

Upload the CSV file through the data import form. If all goes well, the import report will show links to imported works.
