Introduction for Music Publishers
=================================

Django Music Publisher is an open source software for original music publishers. It is based on Django Web framework, a free and open source marvel.

Django Music Publisher is a tool for **managing metadata** on musical works and recordings, including data on writers, recording and performing artists, albums and music libraries, as well as **royalty distribution processing**.

It uses **Common Works Registration (CRW)** protocol for batch registartions of musical works. 

Built by an experienced developer with over 12 years of experience in music publishing, it focuses on doing several crucial tasks in music publishing effectivelly and integrates well with similar tools.

Project Scope
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django Music Publisher will always support **only original publishers**, covering the special situation in the US, where a publisher may have separate entities in each of the PROs. It is not intended to be used by administrators or sub-publishers.

Current Features
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The database holds data on musical works and recordings, including alternate titles, title of original work for modified works, data on writers, recording and performing artists, albums and music libraries, as well as CWR exports and registration acknowledgements.

Multiple writers, both controlled and uncontrolled, are covered, with minor limitations, but data on other publishers (other original publishers, administrators and sub-publishers) can not be entered.

This translates to the following CWR 2.x / 3.0 transaction record types:

======================================  =====================================
CWR 2.1 / 2.2                           CWR 3.0 (still in draft)
======================================  =====================================
NWR/REV                                 WRK, XRF
SPU, SPT (just World)                   SPU, SPT
SWR, SWT (just World), PWR, OWR         SWR, SWT (just World), PWR, OWR, OWT
ALT, PER, REC (single), ORN (only LIB)  ALT, PER, REC (single), ORN (only LIB) 
======================================  =====================================

Please note that **CWR 3.0 has not yet been released**. It will be implemented as
soon as the official documentation gets published.

Basic publishing agreement data can be entered, sufficient for registrations in societies that require society-assingned agreement numbers and for a simple royalty distribution processing. 

It can take data from a spreadsheet (CSV or Excel) file and augment this data with the data from the database. This data can be used in pivot tables for creation of client statements and for accounting.

Presumptions and Limitations
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

It is presumed that writers own and collect 50% of performing rights and the other 50%, as well as 100% of mechanical and sync are owned and collected by publishers. While there are exceptions, this is how most publishers work. 

It skips a lot of rarely used fields, leaving the values blank. When the fields are required in CWR, it uses reasonable defaults, e.g.:

* Musical Work Desitribution is set to Unclassified
* Recorded indicator is set to Uknown if no recording has been entered and to Yes if it has been entered
* Grand Rights Indicator is set to No
* Reversionary Indicator is left empty
* First Recording Refusal Indicator is set to No
* Work for Hire is left empty

Virtually all original publishers in production music and vast majority of small ones in commercial music work this way.

If this is not how you work, then this is not the tool for you, but you are free to extend it for your needs.


Deployment options
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Publishers have several deployment options:

* installed on a local computer (not recommended for real work)
* custom VPS installation (requires basic sysadmin skills)
* installation on Heroku, Dokku, etc. (also requires some sysadmin skills)
* use of a speciallised commercial service (currently only `DMP Guru <https://dmp.guru/>`_)

