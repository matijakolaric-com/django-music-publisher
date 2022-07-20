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

.. mermaid::
    :caption: Simplified Class Diagram
    
    classDiagram
        direction BT
        class Writer {
            first name
            last name
            IPI
            CMO aff.
            ...
        }
        class Work {
            title
            ISWC
            ...
        }
        class Recording {
            recording title
            version title
            ISRC
            ...
        }
        class Artist {
            first name
            last/band name
            ISNI
            ...
        }
        class GeneralAgreement {
            publisher fee
            ...
        }
        class WriterInWork {
            role
            manuscript share
            controlled
            ...
        }
        class Release {
            title
            date
            ...
        }
        class Label {
            name
        }
        class Library {
            name
        }
        GeneralAgreement --> Writer
        Writer <-- WriterInWork
        WriterInWork --> Work
        Label <-- Recording : Record Label
        Recording --> Work
        Recording --> Artist: Recording Artist
        Artist <..> Work : Live Artist
        Release <.. Work : Library Release
        Release <--> Recording : Track
        Release ..> Library : Library Release
        Release --> Label : Release Label

Common Works Registration (CWR)
+++++++++++++++++++++++++++++++++

It implements `CWR protocol <https://matijakolaric.com/articles/1/>`_
for **batch registration of musical works** with Collective Management Organizations 
(CMOs) and Digital Service Providers (DSPs).

.. mermaid::
    :caption: Sequence diagram: Work registration and incoming royalty statements

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

Incoming data is accepted
as a CSV file. If registrations are done using CWR, 
work matching is fully automatic. 
Output is a similar CSV file with additional rows and columns.

.. mermaid::
    :caption: Sequence diagram: Processing incoming royalty statements

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