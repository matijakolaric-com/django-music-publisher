Release Policy
##############

Features Releases
=================

There were 4 releases with new features in 2018.
Since 2019, there are two releases per year with new features, in January and July. Here is a brief overview.

18.7 - 18.11
------------

Initial release in July 2018 had a very simple data structure. It used external API
for CWR generation. The code was open-source, but it was dependant on a commercial service.

Features were gradually added. Support was added for multiple US publishers, removed later.

19.1 Epiphany
-------------

CWR generation and complete data validation was added to the open-source code. Full support for
modified works was added, as well as basic co-publishing support.
Two JSON formats were added (one has been removed since).

19.7 Metanoia
-------------

Multiple recordings per work can be added. CWR 3.0 generation was added, labeled as "experimental".
CWR preview, for both versions, now includes basic syntax highlighting. CWR files are now zipped before the download.

Support for US publishers with entities in different PROs was dropped.

20 Twenty
---------

Twenty-twenty can now be deployed to the free tier of Heroku by non-techies and Heroku API
can be used for maintenance.

Support for custom global share splits was added, solving compatibility issues with some societies.
This also requires MR/SR affiliations for writers, so that was added as well.

Normalized JSON export was dropped.

20.7 and beyond
---------------

The main areas for further development are:

* Royalty distribution
* DDEX (MWN/RIN) support
* CWR 3.x

Minor Releases
==============

Minor releases are bugfix/security releases.

They are released when a real security issue is detected in Django-Music-Publisher or any of the dependencies.
Bugfixes are released when needed, the speed of it depends on the severity of a bug.
