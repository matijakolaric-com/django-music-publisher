Release Policy
##############

Major versions of DMP are released in January and July. Minor versions of the latest major version,
containing bug fixes and/or security updates, are released as required.


Major Release History
=====================

18.7 - 18.11
------------

Initial release in July 2018 had a very simple data structure. It used external API
for CWR generation. The code was open-source, but it was dependant on a free tier of a commercial service.

19.1 Epiphany
-------------

This version was focused on making DMP completely independent of any software not available as open-source 
and compatible with the MIT license.

CWR generation and complete data validation was added to the open-source code. Full support for
modified works was added, as well as basic co-publishing support. Data export in JSON format was added.

19.7 Metanoia
-------------

This version was about making DMP compatible with both current and future requirements within the precisely defined scope.

Most notably, support for multiple recordings per work and CWR 3.0 (labeled as "experimental") were added.
CWR preview, for both versions, received basic syntax highlighting. Since this version, CWR files are zipped.

20 Twenty
---------

Twenty-twenty was primarily about simplified deployment. Since this version, DMP can be deployed to the Free Heroku dyno
(container) by non-techies.

Support for custom global share splits was added. MR/SR affiliations for writers were also added. Syntax highlighting for 
CWR acknowledgements was added, to simplify dealing with conflicts and other registration-related issues.

20.7 Endemic
------------

This version added a lot of new features!

Processing of royalty statements is the most important new feature since the 
initial release. It can import statements in practically **any** CSV format. Processing is
extremely fast.

Basic CSV imports and exports for musical works, and JSON exports for releases were added.

ISWCs can now be imported from CWR acknowledgements. Controlled writers with no society 
affiliation are now fully supported.

Index (home) page became clearer due to grouping of views. User manual was reorganised to follow
the same structure. ``User manual`` links now lead to the relevant page in the user manual.


21.1 Victor (current)
---------------------

This version was focused on improving and extending existing features.

Support for CWR was extended to include latest revisions:

* CWR 2.1 Revision 8
* CWR 2.2 Revision 2 (includes cross-references)
* CWR 3.0 Revision 0 (includes cross-references, experimental)
* CWR 3.1 DRAFT (includes cross-references, experimental)

CWR Syntax highlighting was improved and now includes all fields DMP generates from data, with more detailed descriptions on mouse-over, for all supported CWR versions.

A side menu was added to all add/change/view pages, making navigation faster. 

21.7 (upcoming)
-------------------------------------------

The upcoming major version will primarily focus on improving data exchange with
other solutions.

It will contain following improvements, already present in the current minor version:

* More data in CSV export: separate performance, mechanical and sync shares for writers
* Support for writers with IPI numbers, but without affiliation

Features planned for the upcoming major version:

* Even more data in CSV exports:

  * recordings, all fields, including recording ID
  * publishers (for controlled writer, name, IPI name #, shares)
  * society work IDs

* More data in CSV imports:

  * recordings, all fields, including recording ID
  * society work IDs

These improvements will ensure bidirectional data exchange between Django-Music-Publisher
and `That Green Thing <https://matijakolaric.com/thatgreenthing>`_.

We are considering following improvements:

* *Go Dutch* mode, where the sum of shares for writers adds up to something else than 100%
  (66.66% for BUMA/STEMRA affiliates)

* Data imports from various 3rd-party formats

* Data exports to various 3rd-party formats

Future open-source features
===========================

There is a business model behind Django-Music-Publisher. In order for a feature to be
released as open-source code, all of the following must apply:

* Code must be global, or near-global. Features that apply to one or couple of 
  countries will not be included.
  E.g. there are several PROs in the US, and they have rules about publishers being affiliated 
  with the same PRO as writers. The consequence is that US publishers usualy have several
  entities, one for each of the PROs. Support for US publishers with multiple entities will not
  be included in open-source code.

* Code must be applicable to small publishers (and soon labels). The goal is to help them
  grow. If a feature is required only by established companies, it will not be included. 
  E.g. features for administrators and sub-publishers will not be included in open-source code.

* A feature must not require complex customisations or deployments.
  Open-source solutions for end-users must be deployable by end-users.
  E.g. licencing of production music or password reset.

