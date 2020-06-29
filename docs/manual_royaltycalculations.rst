Royalty Calculations
==============================

Publishers receive royalty statements and payments from collective
societies, DSPs, administrators, sub-publishers, etc. They usually
keep only part of the revenues, while the rest is distribute to clients.

For this, outgoing royalties must be calculated. These calculations are
the basis for outgoing statements and payments.

Django-Music-Publisher is fast and precise in calculating royalties. And
it does only this crucial part. 

Generation of outgoing royalty statements, and sometimes even pre-processing,
can be performed in more suitable tools, e.g. Excel.

Process overview
-----------------------------------------

After the user selects a CSV file and appropriate values for all fields 
and submits, the resulting CSV file is downloaded.

It has all the columns from the incoming file plus several more. For one 
row in the incoming file, the resulting file will have one or more rows.

.. note::
   No changes to the database occur during this process. Incoming file is
   only temporarily saved to the server filesystem. Outgoing file is never saved.

Preparing the ingoing CSV file
-----------------------------------------

In most cases, no pre/processing is required. Most of societies and other 
senders of royalty statements have an option of sending them in CSV format. 

Other formats can be converted to CSV.

Sometimes it is required to remove some data from the incoming file,
or split it in several files to be processed differently. This can
usually be done in Excel.

Algorithms
-------------------------------------------

In both algorithms, user has to select:

* column containing the identifier
* type of identifier (internal work ID, sender's work ID, ISWC, ISRC)
* column containing the amount

Split by calculated share
+++++++++++++++++++++++++++++++++++++++

In this algorithm, one additional information is required, column containing 
the type of right (performance, mechanical, sync) or the type of right applicable to
the whole file.

The amount in each row, depending on the right, is then split among controlled writers
and the publisher. For each incoming row, each controlled writer in work receives one 
row in the output file, and so does the publisher.

Split by manuscript share and apply fees
++++++++++++++++++++++++++++++++++++++++++++++++++++

This is default algorithm.

One additional information is required, **default publisher fee**, to be used
when the fee is set neither in the ``writer in work``, nor in the ``writer``.

For each incoming row, each controlled writer in work receives one row in the output file. 
The amount is split among controlled writers, based on their relative manuscript shares. The
fee is deducted from this gross amount, resulting in net amount to be paid to the writer.

Publisher fee is taken from the first available of:

* `writer in work`
* `writer (for general agreements only)
* `default publisher fee` from this form

.. note::
    If publisher fee is empty, it is not used, and the next option is taken.
    If it has value 0, then no fee is applied (zero fee), and next option is not considered.
    
Post-processing
-------------------------------------------------
