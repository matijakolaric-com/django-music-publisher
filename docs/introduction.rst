Introduction
=================================

Django-Music-Publisher (DMP) is open source software for **managing music metadata**,
(works, writers, recordings, artists, labels, releases and libraries). It uses
`Common Works Registration (CWR) <https://matijakolaric.com/articles/1/>`_
for batch registration/licencing of musical works with collective management organizations (CMOs, AKA PROs, MROs,
collecting societies, etc.) and DSPs, as well as data delivery to sub-publishers.

Django-Music-Publisher is based on `Django web framework <https://www.djangoproject.com/>`_, hence the name.

Project Scope
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django-Music-Publisher can be used out-of-the-box by most small original publishers, both in commercial and production music. Others can use it as a proof-of-concept for custom development.

Each Django-Music-Publisher instance supports a **single original publisher**. It is not intended to be used by administrators or sub-publishers, nor by publishing companies with multiple entities.


Features
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The database contains detailed metadata for **musical works** and **recordings**, data about
**writers**, recording and performing **artists**, **releases** (albums) and **music libraries**,
as well as **CWR exports**, **registration acknowledgements** and **ISWC assignments**.

All entered data is validated for CWR compatibility on field-, record- and transaction-level. Different societies
(collecting organizations) have slightly different requirements. This can be configured in the settings.

Basic original publishing agreement data can be entered, sufficient for registrations in societies that require
society-assigned agreement numbers.

Shares split between the publisher and controlled writers can be configured, in accordance with national regulations
and customs.

Data is also sufficient for simple royalty distribution processing, which is not yet fully implemented.

Registrations can be exported as CWR 2.1 (zipped) files. Acknowledgement files in CWR format can be imported.
CWR preview features syntax highlighting with additional data on mouse-over.
There is an experimental support for and CWR 3.0, including ISRC requests.

New works can be imported from a CSV format. Data for selected works can be exported as JSON.

Limitations
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django-Music-Publisher does not manage data for "other" publishers. Co-publishing deals are still possible, with each
publisher registering their own shares. Shares split between the controlled original publisher (you) and controlled writers is global.
Composite musical works, as well as recordings based on multiple musical works (e.g. medleys), are not supported.

When creating CWR, many fields are left with blank/zero values. When the fields are required in CWR, it uses reasonable defaults, e.g.:

* *Musical Work Distribution* is set to *Unclassified*
* *Recorded indicator* is set to *Yes* or *Unknown*, depending if a recording was entered
* *Work for Hire*, *Grand Rights Indicator*, *Reversionary Indicator*, and *First Recording Refusal Indicator* are set to No

Importing work IDs from other systems is not supported.
