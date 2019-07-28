Release Policy
##############

Django Music Publisher release policy defines how and when new versions are released, as well as their naming. We have major and minor releases. Major releases have two segments in version identifier, the year and the month of the release.

Minor releases have three segments, the first two are the same as the current major release, while the third is incremental numbering.

Major Releases
==============

There are two reasons for a major release:

* Every two years, a new long term support (LTS) version of Django is released, in April of the odd year. There will be a new Django Music Publisher release several months later.

* New features of Django Music Publisher depend on sponsors. If there is enough financing for a new feature, there will be a sponsored major release.

Current Major Release
+++++++++++++++++++++

Current major release is |version|.

Changes from 19.1
+++++++++++++++++++++++

Support for US publishers with entities in different PROs was dropped. If you need to manage multiple publishing entities, you need to run multiple instances of DMP and manage them separately.

Multiple recordings per work can be added. But medleys are still not supported, nor will ever be.

CWR 3.0 generation was added, though labeled as "experimental". CWR 2.1 generation is still available, but it does not contain album data. Collecting societies decided not to use release/album data in work registrations any more. Django Music Publisher 19.7 maintained and extended the data structure dedicated to releases. It will become useful with additional modules.

CWR preview, for both versions, now includes basic syntax highlighting.

All exports, two JSON formats and two CWR versions, are now based on a single data structure, which is becoming the default for other tools and services by the maintainer.

General documentation is now shorter, but more precise. User manual was rewritten and extended.

Minor Releases
==============

Minor releases are bugfix/security releases.

They are released when a real security issue is detected in Django Music Publisher or any of the dependencies. Bugfix releases are released as bugs get fixed, the speed of it depends on the severity of a bug.
