Introduction
============

Django Music Publisher is an open source Django app for original music publishers. 

At this point, it covers all the data required for batch (CWR) registrations of musical works, as well as basic data on agreements between the publisher and writers.

An external, commercial service is used for data validation and CWR generation. Django Music Publisher can work without it, but data will not be validated as CWR-compliant, and there will be no way to export CWR.

Project Scope
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django Music Publisher will always support only original publishers, with the special situation for the US, where a publisher may have separate entities in each of the PROs. It is not intended to be used by administrators or sub-publishers.

Current Features
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

**Original publishers**, publishing only **original musical works**, will find the current features sufficient for registration at all societies that receive batch registrations of musical works in CWR format.

The database holds data on musical works, including alternate titles, songwriters, performing artists, first recordings (including recording artists), music libraries and albums, as well as CWR exports and registration acknowledgements.

Multiple writers, both controlled and uncontrolled, are covered, with minor limitations, but data on other publishers (other original publishers, administrators and sub-publishers) can not be entered.

This translates to following CWR 2.x / 3.0 transaction record types:

======================================  =====================================
CWR 2.1 / 2.2                           CWR 3.0 draft
======================================  =====================================
NWR/REV                                 WRK, XRF
SPU, SPT (just World)                   SPU, SPT
SWR, SWT (just World), PWR, OWR         SWR, SWT (just World), PWR, OWR, OWT
ALT, PER, REC (single), ORN (only LIB)  ALT, PER, REC (single), ORN (only LIB) 
======================================  =====================================

A special **US** situation where the original publisher may have one entity for every of the three PROs is also covered.

It is presumed that writers own and collect 50% of performing rights and the other 50%, as well as 100% of mechanical and sync are owned and collected by the original publisher. While there are exceptions, this is how things usually work.

Basic publishing agreement data can be entered, but currently no statement processing capabilities are included.

Ideas and plans
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Following features are required in order to make Django Music Publisher completely free and available to small music publishers without any limitations:

* Adding custom work IDs
* Adding data imports, requires custom work IDs
* Including complete validation, CWR generation and highlighting in the open source
* Adding MWN (DDEX)
* Including modifications of musical works
* Royalty statement processing
* Extending the features towards the recording/labes side of music rights
* Implementing other DDEX formats/processes
* Simplified deployment

Looking for sponsors/donators.
