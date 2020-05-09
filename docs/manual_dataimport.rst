Importing Data
==============================

Simple musical works can be imported from a CSV file. The template is provided.

Caveats
-------------------

Who should import data?
_______________________

Data imports should not be regarded as a part of the standard work flow and should not be performed by staff users.
Many failsafes, present during the manual data input and editing, are not available during data imports.
Therefore, the default user groups ``Publishing Staff`` and ``Publishing Audit`` don't allow importing.

There is no way to undo a successful import other than by restoring your database from a
backup. If you don't know how to back up and restore your database, do not import data!

What is being imported?
_______________________

The import process will add works, including alternative titles, writers, artists, libraries
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

All imported works get **new work IDs**. If you already registered these works with different work IDs, this
**will** result in double registrations. If new work IDs are the same as the ones you used before, then old
registrations **will** be overwritten.


How to import?
------------------------------

Open the spreadsheet template. Fill out the ``Registrations`` sheet. Save this sheet as CSV.

Then upload the CSV file through the data import form. If all goes well,
the report will show the link to imported works.
