Release History
#####################

Django-Music-Publisher was originally released in July 2018, and 
for the rest of 2018, development was very rapid, with major 
improvements being released in August, September and November.

From January 2019 to January 2022, major versions were released 
twice per year.

Minor versions, with bug fixes and security updates, are
released when required. They are not mentioned in this document.


Major Release History
=====================

18.7 - 18.11
------------

Initial release in July 2018 had a very simple data structure. 
It used external API for CWR generation. The code was open-source, 
but it was dependant on a free tier of a commercial service.


19.1 Epiphany
-------------

This version was focused on making DMP completely independent of 
any software not available as open-source and compatible with the
MIT license.

CWR generation and complete data validation was added to the 
open-source code. Full support for modified works was added, as 
well as basic co-publishing support. Data export in JSON format 
was added.

19.7 Metanoia
-------------

This version was about making DMP compatible with both current 
and future requirements within the precisely defined scope: 
**single publisher**, **single manuscript share**. 
(This scope has not changed since, nor will in the future.)

Most notably, support for multiple recordings per work and 
CWR 3.0 (labeled as "experimental") were added. CWR preview, for 
both versions, received basic syntax highlighting. Since this 
version, CWR files are zipped.

20 Twenty
---------

Twenty-twenty was primarily about simplified deployment. Since 
this version, DMP can be deployed to the Free Heroku dyno
(container) by non-techies.

Support for custom global share splits was added. MR/SR 
affiliations for writers were also added. Syntax highlighting for 
CWR acknowledgements was added, to simplify dealing with conflicts 
and other registration-related issues.

20.7 Endemic
------------

This version added a lot of new features!

Processing of royalty statements is the most important new feature 
since the initial release. It can import statements in practically 
**any** CSV format. Processing is extremely fast.

Basic CSV imports and exports for musical works, and JSON exports 
for releases were added.

ISWCs can now be imported from CWR acknowledgements. Controlled 
writers with no society affiliation are now fully supported.

Index (home) page became clearer due to grouping of views. User 
manual was reorganised to follow the same structure. ``User manual``
links now lead to the relevant page in the user manual.


21.1 Victor
---------------------

This version was focused on improving and extending existing 
features.

Support for CWR was extended to include latest revisions:

* CWR 2.1 Revision 8,
* CWR 2.2 Revision 2 (includes cross-references),
* CWR 3.0 Revision 0 (includes cross-references, experimental), and
* CWR 3.1 DRAFT (includes cross-references, experimental).

CWR Syntax highlighting was improved and now includes all fields 
DMP generates from data, with more detailed descriptions on 
mouse-over, for all supported CWR versions.

A side menu was added to all add/change/view pages, making 
navigation faster. 

21.5 Mayday
-------------------------------------------

The version focuses on improving data exchange with other 
solutions, most notably `That Green Thing 
<https://matijakolaric.com/thatgreenthing>`_.

* Support for writers with IPI numbers, but without CMO 
  affiliations was improved
* Internal notes for writers, artists and labels were added

* More data is available in CSV exports:

    * separate manuscript, performance, mechanical and sync 
      shares for writers,
    * data about an original publisher, with performance, 
      mechanical and sync shares,
    * data about recordings, including recording ID, record 
      labels and recording artists, and
    * society Work IDs.

* More data is available in CSV imports:

    * data about recordings: ISRC, duration, release date, and
    * society work IDs.

* Improved support for ISWC imports and duplicate handling.

* Interface now also available in *dark* mode

22.1 Exofile
----------------------------

With very little to do in the realm of music publishing, within 
the defined scope, DMP has moved towards supporting music companies
who are **both publishers and labels**.

This version added support for file uploads, either locally (for 
traditional installations) or to S3 storage (for containers). Please
consult :doc:`installation` for instructions how to enable and 
configure file storage.

Writers, artists, labels and releases received ``image`` and 
``description`` fields, to be used in front-end representations.
Recordings received an ``audio_file`` field.

Read-only REST API endpoints are available for releases and recording artists,
enabling integration with websites.

Playlists can now be created, either by manually adding recordings,
or by using batch actions in various list views, and shared
using secret URLs.

Full metadata backup can be download using REST API endpoint.

22.9 Rubicon
-------------------------------

``Account #`` field was added to the writer model. This field can be used for linking
data from outgoing royalty statements with accounting.

Many of the improvements in this release are under the bonnet. The code has been 
reviewed and partly cleaned up. Code style is now validated with Black.

Introduction chapter of this documentation was extended with graphs, and split 
into two separate documents.




Future open-source features
===========================

Rules
---------------------------

In order for a feature to be released as open-source code, all of 
the following must apply:

* Code must be global, or near-global. Features that apply to one 
  or a couple of countries will not be included.

* Code must be applicable to startup music companies. The goal is 
  to help them grow. If a feature is required only by established 
  companies, it will not be included. 

* A feature must not require complex customisations or deployments.
  Open-source solutions for end-users must be deployable by 
  end-users.
