Importing Data
==============================

Simple musical works can be imported from a CSV file. This advanced functionality is considered
**experimental**.

Caveats
-------------------

Who should import data?
_______________________

Data imports should not be regarded as a part of the standard work flow and should not be performed by
staff users.
Many failsafes, present during the manual data input and editing, are not available during data imports.
Therefore, the default user groups ``Publishing Staff`` and ``Publishing Audit`` don't allow importing.

There is no way to undo a successful import other than by restoring your database from a
backup. If you don't know how to back up and restore your database, do not import data!

What is being imported?
_______________________

The import process will *add* works, including alternative titles, writers, artists, libraries
and library releases.

No data is changed, with only one exception. A general agreement for an existing writer may be set and a
society-assigned agreement number may be added.

Why are errors reported?
_________________________

If data in the file is incomplete or conflicting with data in the database (or other data in the
same file), an error will be thrown. Not all errors are returned in a user-friendly way.

When an error is thrown, no changes to the database occur.

Work IDs
________

The template contains ``Work ID`` column. If you never gave your works your own IDs, leave this blank.
The system will generate work IDs. Note that this is *not* the ID given by your society or any third party.

On the other hand, work IDs must be maintained when moving from one software to another. Failing to do so
may overwrite your existing registrations at collecting societies or create duplicates.

How to import?
------------------------------

Creating a template
______________________________

First, you are advised to create a template. To do that, export several works as CSV,
as described in :ref:`exporting_csv`.

Open the file in your spreadsheet editor and save in the native format. Then delete the data and save again.
Use the first file as an example and the second one as a template.

Repeating column groups for alternate titles, writers and artists are created so that the selected data can fit.
You can create additional columns by copying the column group and giving it a different counter.
(Alt Title 1, Alt Title 2, Writer 1, Writer 2, Artist 1, Artist 2). There is no limit to the number of column groups.


Filling out the template
______________________________

Open the spreadsheet template. Fill out the ``Registrations`` sheet. Save this sheet as CSV.

Values in ``Writer PRO``, ``Writer Role`` and ``Writer Controlled`` columns must
start with correct codes. ``10``, ``10 ASCAP``, ``10 - ASCAP`` or ``10 - BMI`` will all resolve as ASCAP.
``ASCAP`` without the code will throw an error. You can get all the codes from the source or by creating a CSV export
example, as described before.

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