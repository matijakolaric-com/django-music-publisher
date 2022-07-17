Introduction
=================================

Music Metadata Management
+++++++++++++++++++++++++++++++++

**DMP** (Django-Music-Publisher) is free, open-source software for **managing music 
metadata**:

* musical works and recordings (with audio files),
* writers, artists and labels (with photos/logos),
* releases/albums (with cover art), and
* music libraries.

Common Works Registration (CWR)
+++++++++++++++++++++++++++++++++

It implements `CWR protocol <https://matijakolaric.com/articles/1/>`_
for **batch registration of musical works** with Collective Management Organizations 
(CMOs) and Digital Service Providers (DSPs).

.. mermaid::

    sequenceDiagram
        Note over Publisher,CMO: Registrations
        Publisher->>CMO: CWR (Work Registration)
        CMO->>Publisher: CWR ACK 1 (Technical validation)
        CMO->>Publisher: CWR ACK 2 (Registration status + CMO work ID + ISWC)
        Note over Publisher,CMO: Royalties
        CMO->>Publisher: Royalty Statement (CMO work ID + royalty amount)

Royalty Management
+++++++++++++++++++++++++++++++++

Simple **royalty management** calculations can split received royalties among controlled 
writers and calculate publisher fees. 

The incoming data is accepted in
as a CSV file, and the output is a similar CSV file with additional rows and
columns.

.. mermaid::

    sequenceDiagram
        CMO/DSP->>Publisher DMP: Incoming Royalty Statement (CSV)
        Publisher DMP->>Publisher Excel: Augmented royalty information
        Publisher Excel->>Writer: Outgoing Royalty Statement
        Publisher Excel->>Accounting: Accounting data

This file can be then imported into excel and turned into individual
outgoing statements and accounting data using pivot tables. This process
can be automated using simple scripts.

Data Distribution
++++++++++++++++++++++++++++++++++

Besides the aforementioned CWR protocol, music metadata can be exported in 
several other formats, or be accessed through the read-only 
:doc:`REST API <restapi>`.