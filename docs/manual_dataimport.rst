Importing Data
==============================

Simple musical works can be imported from a CSV file.

Caveats
-------------------

Who should import data?
_______________________

Data imports should not be regarded as a part of the standard work flow and should not be performed by
staff users.

Failsafes, present during the manual data input and editing, may not be available during data imports.

.. warning:: There is no way to undo a successful import other than by restoring your database from a backup. If you don't know how to back up and restore your database, do not import data!

What is being imported?
_______________________

The import process will *add* works, including alternative titles, writers, artists, libraries
and library releases.

No data is ever *modified*, with only one exception. A general agreement for an existing writer may be
set and a society-assigned agreement number may be added.

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

Download `CSV Template <work_import_template.csv>`_.
You can edit it in Excel or another spreadsheet tool. 

It contains 4 columns for alternate titles, as well as
4 column sets for writers and 4 column sets for artists.

For another writer column set, add all of:
``Writer 5 Last``, ``Writer 5 First``, ``Writer 5 IPI``, ``Writer 5 PRO``, ``Writer 5 Role``,
``Writer 5 Share``, ``Writer 5 Controlled``, ``Writer 5 SAAN``

Note that this file has the same form as CSV exports, described in :ref:`exporting_csv`.

Filling out the template
______________________________

Fill out the template. Make sure to save as CSV.

Values in ``Writer PRO``, ``Writer Role`` and ``Writer Controlled`` columns must start with correct codes.

``Writer PRO`` must start with society code without the leading zero.
``10``, ``10 ASCAP``, ``10 - ASCAP`` or ``10 - BMI`` will all resolve as ASCAP. ``ASCAP`` without the code
will throw an error.

``Writer Role`` must start with one of ``C``, ``A``, ``CA``, ``AR``, ``TR``  or ``AD``.

``Writer Controlled`` should be set to ``No``, ``Yes`` or ``General``.

Data upload
______________________________

Upload the CSV file through the data import form. If all goes well,
the import report will show links to imported works.

Professional support
--------------------

The creator of Django-Music-Publisher runs a `professional support service <https://matijakolaric.com/dmp-prosupport/>`_
for users of DMP. Subscribers can receive support with all aspects of data import,
including a professionally made spreadsheet template.

.. figure:: /images/import_template.png
   :width: 100%

   Professionally made import template with basic validation.