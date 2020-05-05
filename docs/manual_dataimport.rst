Importing Data
==============================

Simple musical works can be imported from a CSV file. The template is provided.

Caveats
-------------------

**Data import is not a replacement for manual editing!**

**Always backup the database before running a data import!**

Data imports should not be regarded as a part of a general work flow. Many failsafes, present during the manual data
input and editing, are not available during data imports.
Data imports should not be performed by normal staff users. The default user groups ``Publishing Staff`` and
``Publishing Audit`` don't allow importing.

The import process will not only add works, including alternative titles, but also add writers and artists, libraries
and library releases.

No data is changed, except that a general agreement for an existing writer may be set and a society-assigned agreement
number may be added to it, if present. If data in the file is conflicting with data in the database, or other data in the
same file, an error will be thrown. Not all errors are returned in a user-friendly way.

If an error is thrown, no changes to the database occur.

All imported works will get **new work IDs**. If you already registered the works being imported with different work IDs, this
may result in double registrations. If new work IDs are the same as the ones you used before, then old
registrations will be overwritten. This usually only refers to electronic batch registration (via CWR, EBR, CSV, etc.),
not manual registration through society portals. So, if this is the first software you use for registrations, you should
be fine.

How to import?
------------------------------

Open the template with free LibreOffice Calc or an alternative. Fill out the ``Registrations`` sheet.
Use ``Save a copy`` and save this sheet as CSV.

Then upload this file through the data import form. If all goes well, the report will show the link to imported works.
In not, good luck with debugging.
