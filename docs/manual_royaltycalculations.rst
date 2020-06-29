Royalty Calculations
==============================

DMP is extremely fast in calculating royalty distributions. Incoming
royalty statements in almost any CSV format can be processed. Output
will be in a similar CSV format, with several additional columns.

Incoming formats
----------------------------------------

Incoming statement must be a CSV file with a header row. 
It can have any number of columns, in any order, as long as it has:

* a column with one of these identifiers:

  * internal work ID
  * sender's work ID, imported through work acknowledgements
  * ISWC
  * ISRC

* a column with amount to be distributed, values must be numeric

Values for these columns must be present in all rows.
   
In most cases, no pre-processing is required. Most of societies and other 
senders of royalty statements have an option of sending them in CSV format. 

Outgoing formats
------------------------------------------

Outgoing format is a CSV file. It has all the columns of the incoming file.
Each incoming row will be copied for every participant who shares in distribution. 
Additional data will be provided in additional columns at the end.

Additional columns depend on the used algorithm.

Algorithms
-------------------------------------------

DMP has two different algorithms for calculating royalty distributions.

In both algorithms, user has to select:

* column containing the identifier
* type of identifier
* column containing the amount

Both algorithms add these columns:

* Controlled by publisher (%)
* Interested party
* Role
* Net amount

Split by calculated share
+++++++++++++++++++++++++++++++++++++++

In this algorithm, one additional information is required:

* **column** containing the type of right (performance, mechanical, sync) or 
  **the type of right** applicable to the whole file.

The amount in each row is split between controlled writers and the publisher,
using the publishing agreement shares from the settings and manuscript shares.

Outgoing rows are generated for each controlled ``writer in work`` and the publisher.

In addition to columns added by both algorithms, this one also adds:

* Right type
* Owned Share (%)
* Share in amount received (%)

Split by manuscript share and apply fees
++++++++++++++++++++++++++++++++++++++++++++++++++++

This is default algorithm.

One additional information is required:

* **default publisher fee**, to be used
  when the fee is set neither in the ``writer in work``, nor in the ``writer``.

For each incoming row, each controlled writer in work receives one row in the output file. 
The amount is split among controlled writers, based on their relative manuscript shares. The
fee is deducted from this gross amount, resulting in net amount to be paid to the writer.

Publisher fee is taken from the first available of:

* ``writer in work``
* ``writer`` (for general agreements only)
* ``default publisher fee`` from this form

.. note::
    If publisher fee is empty, it is not used, and the next option is taken.
    If it has value 0, then no fee is applied (zero fee), and next option is not considered.

In addition to columns added by both algorithms, this one also adds:

* Manuscript share (%)
* Share in amount received (%)
* Amount before fee
* Fee (%)
* Fee amount

Post-processing
-------------------------------------------------

Excel or an alternative is the best tool for post-processing,
especially creating outgoing statements.

Outgoing royalty statements
+++++++++++++++++++++++++++++++++++++++

For creating outgoing statement, use pivot tables, filtering by 
``Interested party`` column. You can design outgoing statemens
however you wish.

Foreign currencies
+++++++++++++++++++++++++++++++++++++++

All amounts calculated by DMP are in the same currency as the incoming data.
Use a dedicated exchange rate table and VLOOKUP function for conversions.

Precision
+++++++++++++++++++++++++++++++++++++++

For calculations, precision exceeds the number of decimal places in any currency.
You are advised to round up only the totals, not the amounts in rows.

