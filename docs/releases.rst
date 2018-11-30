Future Releases and Sponsored Features
######################################

Major releases
==============

The purpose of major releases is to keep up with projects and specifications Django Music Publisher depends on. Basically, this boils down to Django, Python and PostgreSQL versions, as well as CWR and DDEX specifications.

The plan is to have two major releases in 2019, and then one every two years, with Django LTS releases. This is due to the fact that CWR 3.0 is going to be released soon, as well as new DDEX versions. Also, MLC may come up with a new set of requirements in the next year, but once all of that is done, we will most likely return to the slow progress of the industry.

=======  ================================================================  ==========  ==========  ==========  ============  =============  ==========
Upcoming Major Releases                                                            Release dates for                         Compatibility
-------------------------------------------------------------------------  ----------------------------------  ---------------------------------------
Version  New features                                                      beta        release c.  stable      Django        Python         PostgreSQL
=======  ================================================================  ==========  ==========  ==========  ============  =============  ==========
19.2     CWR 3.0: ISWC handling, licence reporting;                        12.02.2019  18.02.2019  22.02.2019  2.1, 2.2 LTS  3.5, 3.6, 3.7  9.4 to 9.6
19.7     Django 2.2 LTS                                                    05.07.2019                          2.2 LTS       3.5, 3.6, 3.7 
21.7     Django 3.2 LTS                                                    02.07.2021                          3.2 LTS       3.6, 3.7
=======  ================================================================  ==========  ==========  ==========  ============  =============  ==========

\* Version 18.11 will be delayed, avaiting a bugfix Django 2.1.4 release


Minor Releases - Security and Bugfix
====================================

Minor releases will be either bugfix/security releases and/or sponsored feature releases.

Security releases are released when a real security issue is detected in Django Music Publisher ot any of the dependencies. Bugfix releases are released as bugs get fixed, the speed of it depends on the severity of a bug.

Minor Releases - Sponsored Features
===================================

The maintainer has no interest in developing this project beyond current features without some kind of compensation. The licence permits anyone to fork the project and continue developing it. But since there is a chance that someone will see the benefit in sponsoring further development, here are some development cost breakdowns for several features that have been identified as missing. All sponsored code will, just as the rest of it, be released under MIT licence. No exceptions.

Free CWR
--------

Current version uses an external service for data validation, CWR generation and syntax highlighting. Django Music Publisher began as a proof of concept for this very service and the current version is fulfilling that purpose. 

However, these are the most important features of Django Music Publisher and they belong into the open source code. Here is what needs to be done:

=================================================== =========
Task                                                Cost
=================================================== =========
CWR generation in DMP (with current features)       €500
CWR validation in DMP (with current features)       €1000
CWR syntax highlighting in DMP                      €500
Integration tests                                   €300
Documentation update                                €100
Minor release                                       €100
**Total**                                           **€2500**
=================================================== =========

Modifications of existing works
-------------------------------

The current version of Django Music Publisher has some limitations that are based on the limitations of the lowest tier of the external CWR generating service it uses. One such limitation is that it only allows registration of original musical works, not modifications.

Once the previous feature is finished, it would be simple to extend the functionality so it would include registrations of the modifications of existing musical works, including ones in the public domain. Here is what needs to be done:

========================================================= =========
Task                                                      Cost
========================================================= =========
Original work model and inline, new writer capacit.       €500
Validation rules spanning all NWR/REV, VER, SWR, OWR rows €750
Integration tests                                         €300
Documentation update                                      €100
Minor release                                             €100
**Total**                                                 **€1750**
========================================================= =========

MWN (DDEX)
----------

This is about finding a sponsor and who would be willing to be a guinea pig. If you would like to be both, please contact the maintainer.

Recording-related data and other DDEX formats
---------------------------------------------

All these features would be a great addition, however, it really comes down to the use case someone has in mind. Please contact the maintainer if you would be interested in sponsoring any development of this nature.

Requested Features under consideration
======================================

Data imports
--------------------

Current version does not support data imports from third party software solutions. So far the maintanier has been providing this as a paid service. However, it would be in everyone interest if people would be able to do it themselves.

There are several caveats here, the first one is related to internal work numbering. If imported data was already used for registrations via CWR or EBR or any format that has submitter work IDs, then they must be maintained. 

Furthermore, it is not the same thing if data is just imported initially or if it is being imported periodically. The latter case should probably include work matching and merging, which is a significant amount of work. 

The third issue is which formats to import. and how to deal with data that Django Music Publisher can not import, such as the data on other publishers. All usual formats hold more data, as they were designed by societies, vendors and large organizations for large publishers, vendors and societies.

The fourth issue is that often the data does not have all the necessary elements for batch registrations.

It is maintainers view that more information is needed on the subject and that the import should be built when people come with real needs and real money.

CWR Delivery service
--------------------

This is definitelly something that would be very helpful. There are three issues here:

* every society and/or administrative agency uses a slightly different delivery system
* this requires some kind of background worker or at least a cron job, so it is a bit more complicated to deploy
* we are deailing with sensitive data here, bad deployments might easily result in security issues, data loss or worse.

Definitelly something to look into. Maybe as a separate package?
