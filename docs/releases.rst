Release Policy
##############

There are two versions per year with new features, in January and July.
Minor versions are released as required.

Past versions with new features
===============================

18.7 - 18.11
------------

Initial release in July 2018 had a very simple data structure. It used external API
for CWR generation. The code was open-source, but it was dependant on a commercial service.

19.1 Epiphany
-------------

CWR generation and complete data validation was added to the open-source code. Full support for
modified works was added, as well as basic co-publishing support.
Data export in JSON format was added.

19.7 Metanoia
-------------

Support for multiple recordings per work and CWR 3.0 generation, labeled as "experimental", were added.
CWR preview, for both versions, received basic syntax highlighting. CWR files are zipped before the download.

20 Twenty
---------

Twenty-twenty was primarily about simplified deployment. Since thsi version, DMP can be deployed to the Free Heroku dyno
(container) by non-techies.

Support for custom global share splits was added. MR/SR affiliations for writers are available when implied by share
split settings.

Syntax highlighting for CWR acknowledgements was added, for simpler dealing with conflicts and other registration-related
issues.

Documentation was completely rewritten.

20.7 Endemic
------------

Index (home) page became clearer, models are split into groups.
CSV export of musical work metadata, import from CSV for *new* musical works, and support for controlled writers with no
society affiliation were added.

Future features
===============

The main areas for further development are:

* Royalty distribution
* DDEX support
* CWR 3.1
