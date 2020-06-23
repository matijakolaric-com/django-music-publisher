Royalty Calculations
==============================

Introduction
-------------------

Publishers receive royalty statements and payments from collective
societies, DSPs, administrators, sub-publishers, etc. They usually
keep only part of the revenues, while the rest is distribute to clients.

For this, outgoing royalties must be calculated. These calculations are
the basis for outgoing statements and payments.

Django-Music-Publisher is fast and precise in calculating royalties. And
it does only this crucial part. Generation of outgoing royalty statements
can then be performed in more suitable tools, e.g. Excel.

Process overview
-----------------------------------------

A brief overview of the royalty calculation process will be given first.

An incoming CSV file is selected for upload, as well as one of two
algorithms. Possible options for other fields are then determined.

After the user selects appropriate values for all fields and submits
the file for processing, the resulting CSV file is downloaded.

The resulting CSV has all the columns from the incoming file plus several
more, depending on the chosen algorithm. For one row in the incoming file,
the resulting file will have one or more rows, depending on algorithm and
the number of controlled writers in a work.

.. note::
   No changes to the database occur during this process. Incoming file is
   only temporarily saved to the server filesystem. Outgoing file is never saved.

Preparing the ingoing CSV file
-----------------------------------------

Most of societies and other senders of royalty statements have an option
of sending them in CSV format. Other formats can be converted to CSV.

In some cases, you may wish to filter out some rows. E.g. some publishers
keep all of the revenue they receive for performance, as writers receive
their share through societies. In that case, remove all performance-related
rows from the CSV file.









Royalty cal