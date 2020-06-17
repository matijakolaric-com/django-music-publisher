Royalty Calculations
==============================

Introduction
-------------------

Publishers receive royalty statements and payments from collective
societies, DSPs, administrators, sub-publishers, etc.

Publishers usually keep only part of the revenues, while the rest is
distribute to clients.

For this, outgoing royalties must be calculated. These calculations are
the basis for outgoing statements and payments.

Django-Music-Publisher is fast and precise in calculating royalties. And
it does only this crucial part. Generation of outgoing royalty statements
can then be performed in more suitable tools, e.g. Excel.

Process overview
-----------------------------------------

A brief overview of the royalty calculation process will be given first.

Incoming CSV file is selected for upload and one of two algorithms is
selected. The visibility and possible options for other fields are
determined.

Preparing the ingoing CSV file
-----------------------------------------

Most of societies and other senders of royalty statements have an option
of sending them in CSV format. Other formats can be converted to CSV.

In some cases, you may wish to filter out some rows. E.g. some publishers
keep all of the revenue they receive for performance, as writers receive
their share through societies. In that case, remove all performance-related
rows from the CSV file.









Royalty cal