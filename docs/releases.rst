Release Policy
##############

Django Music Publisher release policy defines how and when new versions are released, as well as their naming. We have major and minor releases. Major releases have two segments in version identifier, the year and the month of the release.

Minor releases have three segments, the first two are the same as the current major release, while the third is incremental numbering.

Major Releases
==============

There are two reasons for a major release:

* Every two years, a new long term support (LTS) version of Django is released, in April of the odd year. There will be a new Django Music Publisher release several months later.

* When there are significant new features. Please note that new features of Django Music Publisher depend on sponsors.

Current Major Release
+++++++++++++++++++++

Current major release is 19.7.

Major Changes from 19.1
+++++++++++++++++++++++

Support for US publishers with entities in different PROs was dropped. If you need to manage multiple publishing entities, you need to run multiple instances of DMP and manage them separately.

Multiple recordings per work can be added. But medleys are still not supported, nor will ever be.

Collecting societies decided not to use release/album data in work registrations any more. Django Music Publisher 19.7 maintained and extended the data structure dedicated to releases. It will become useful with additional modules.

All imports and exports, including two JSON formats included in 19.7, are now based on a single data structure, which is becoming the default for other tools and services by the maintainer.

CWR 2.1 generation and acknowledgement parsing is still available. CWR 3.0, labeled as "experimental", is freely available as a separate module.

Minor Releases
==============

Minor releases are bugfix/security releases.

They are released when a real security issue is detected in Django Music Publisher or any of the dependencies. Bugfix releases are released as bugs get fixed, the speed of it depends on the severity of a bug.
