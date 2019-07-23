Introduction
=================================

Django Music Publisher is open source software for original music publishers. It is based on Django Web framework.

Django Music Publisher is a tool for **managing metadata** on musical works and recordings. It has support for **royalty distribution processing**.

It uses **Common Works Registration (CWR)** protocol for batch registrations of musical works.

Built by an experienced developer with over 12 years of experience in music publishing, it focuses on doing several crucial tasks in music publishing effectively and integrates well with similar tools.


Project Scope
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Each Django Music Publisher instance supports a **single original publisher**. It is not intended to be used by administrators or sub-publishers, nor by publishing companies with multiple entities.


Current Features
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The database holds data on musical works and recordings, including alternate titles, title of original work for modified works, data on writers, recording and performing artists, releases (albums) and music libraries, as well as CWR exports and registration acknowledgements.

Multiple writers, both controlled and uncontrolled, are covered, with minor limitations.

This translates to the following CWR 2.x / 3.0 transaction record types:

======================================  ======================================
CWR 2.1 / 2.2                           CWR 3.0
======================================  ======================================
NWR/REV,                                WRK
SPU, SPT (just World), OPU (unknown),   SPU, SPT (just World), OPU (unknown)
SWR, SWT (just World), PWR, OWR,        SWR, SWT (just World), PWR, OWR, OWT
ALT, PER, REC (single), ORN (only LIB)  ALT, PER, REC, ORN (only LIB), XRF
======================================  ======================================

Basic original publishing agreement data can be entered, sufficient for registrations in societies that require society-assigned agreement numbers and for simple royalty distribution processing.

The actual royalty distribution processing is not yet implemented.


Limitations
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django Music Publisher is aiming to be a simple tool that is good enough for most original publishers. Being simple means that there are some limitations.

It does not hold data on "other" publishers. Co-publishing deals are still possible, with each publisher registering their shares.

With default settings, it is presumed that controlled writers own and collect 50% of performing rights and the other 50%, as well as 100% of mechanical and sync are owned and collected by publishers. A different split is possible, but there can only be one for all controlled writers.

When creating CWR, many fields are left with blank/zero values. When the fields are required in CWR, it uses reasonable defaults, e.g.:

* Musical Work Distribution is set to Unclassified
* Recorded indicator is set to Unknown if no recording has been entered and to Yes if it has been entered
* Grand Rights Indicator is set to No
* Reversionary Indicator is left empty
* First Recording Refusal Indicator is set to No
* Work for Hire is left empty

If this is not how you work, then this is not the tool for you, but you are free to extend it for your needs.

CWR automated delivery is not implemented. This is not an issue with CWR 2.1, but in CWR 3.0, the delivery process may be too complicated for manual delivery.

Recordings based on multiple musical works (e.g. medleys) are not supported.

Deployment options
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Publishers have several deployment options:

* installed on a local computer (not recommended for real work)
* custom VPS installation (requires basic sysadmin skills)
* installation on Heroku, Dokku, etc. (also requires basic sysadmin skills)
* to be included in a larger Django project (requires significant coding skills)
* use of a specialised commercial service (currently only `DMP Guru <https://dmp.guru/>`_)

