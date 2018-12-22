Introduction for Music Publishers
=================================

Django Music Publisher is an open source software for original music publishers. It is based on Django Web framework, a free and open source marvel.

At this point, it covers all the features required for batch (CWR) registrations of musical works, as well as basic data on agreements between the publisher and writers.

Project Scope
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django Music Publisher will always support only original publishers, covering the special situation in the US, where a publisher may have separate entities in each of the PROs. It is not intended to be used by administrators or sub-publishers.

Current Features
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

**Original publishers** will find the current features sufficient for registration at all societies that receive batch registrations of musical works in CWR format.

The database holds data on musical works, including alternate titles, songwriters, performing artists, first recordings (including recording artists), music libraries and albums, as well as CWR exports and registration acknowledgements.

Multiple writers, both controlled and uncontrolled, are covered, with minor limitations, but data on other publishers (other original publishers, administrators and sub-publishers) can not be entered.

This translates to the following CWR 2.x / 3.0 transaction record types:

======================================  =====================================
CWR 2.1 / 2.2                           CWR 3.0 draft
======================================  =====================================
NWR/REV                                 WRK, XRF
SPU, SPT (just World)                   SPU, SPT
SWR, SWT (just World), PWR, OWR         SWR, SWT (just World), PWR, OWR, OWT
ALT, PER, REC (single), ORN (only LIB)  ALT, PER, REC (single), ORN (only LIB) 
======================================  =====================================

It is presumed that writers own and collect 50% of performing rights and the other 50%, as well as 100% of mechanical and sync are owned and collected by publishers. While there are exceptions, this is how things usually work.

Basic publishing agreement data can be entered, sufficient for simple royalty distribution processing.

Deployment options
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Publishers have several deployment options:

* installed on a local computer (not recommended for real work)
* custom VPS installation (requires basic sysadmin skills)
* installation on Heroku, Dokku, etc. (also requires some sysadmin skills)
* use of a speciallised commercial service (currently only `DMP Guru <https://dmp.guru/>`_)

