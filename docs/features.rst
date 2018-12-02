Sponsored Features
##################

The maintainer has no interest in developing this project beyond current features without some kind of compensation. The licence permits anyone to fork the project and continue developing it. Here are development cost breakdowns for several features that have been identified as missing. All sponsored code will, just as the rest of it, be released under MIT licence. No exceptions.

Royalty statement processing
----------------------------

There are many different input formats, and they also come in different currencies with different conversion rates at different dates.
As Django Music Publisher is only for original publishers, the only scenario where statement processing makes sense is that part of the revenue has to be passed on to the writers. That is not the case with all users.

The ``publisher fee`` field states the percentage kept by the publisher. A very simple statement processing needs to be able to parse incoming statements, and convert it to a custom spreadsheet format. It really comes down to knowing how to use Excel or some of the alternatives. For someone who knwos how pivot tables work, that is more than enough.

CWR service subscribers also get these features for free, but it would be nice if they would be freely available to the public.

========================================================= =========
Task                                                      Cost
========================================================= =========
Creating a spreadsheet template                           €100
Creating a basic parsing /exporting framework             €750
Creating a custom import (per format)                     €150
Documentation update                                      €100
Minor release                                             €50
**Total**                                                 **€1150**
========================================================= =========


Free CWR
--------

The current version uses an external service for data validation, CWR generation and syntax highlighting. Django Music Publisher began as a proof of concept for this very service and the current version is fulfilling that purpose. 

However, these are the most important features of Django Music Publisher and they belong into the open source code. Here is what needs to be done:

=================================================== =========
Task                                                Cost
=================================================== =========
CWR generation in DMP (with current features)       €500
CWR validation in DMP (with current features)       €1000
CWR syntax highlighting in DMP                      €500
Integration tests                                   €300
Documentation update                                €100
Minor release                                       €50
**Total**                                           **€2450**
=================================================== =========

Modifications of existing works
-------------------------------

The current version of Django Music Publisher has some limitations that are based on the limitations of the lowest tier of the external CWR generating service it uses. One such limitation is that it only allows registration of original musical works, not modifications.

Once the previous feature is finished, it would be simple to extend the functionality so it would include registrations of the modifications of existing musical works, including ones in the public domain. Here is what needs to be done:

========================================================= =========
Task                                                      Cost
========================================================= =========
Original work model and inline, new writer capacities     €500
Validation rules spanning all NWR/REV, VER, SWR, OWR rows €750
Integration tests                                         €300
Documentation update                                      €100
Minor release                                             €50
**Total**                                                 **€1700**
========================================================= =========

Data import
-----------

Current version does not support data imports from third party software solutions or spreadsheet data. So far the maintanier has been providing this as a paid service. However, it would be in public interest if people would be able to do it themselves.

There are several caveats here, the first one is related to internal work numbering. If imported data was already used for registrations via CWR or EBR or any format that has submitter work IDs, then they must be maintained. Second one is that usual formats contain more data then Django Music Publisher can hold. The third issue is that often the data does not contain all the data required for a minimal CWR.

This proposed feature adds custom work IDs, and allows imports from two custom formats, a JSON which is the same format Django Music Publisher exports, as well as a custom spreadsheet format. Any futher format can be added once this has been finished.

========================================================= =========
Task                                                      Cost
========================================================= =========
Creating a spreadsheet template                           €100
Creating import model and interface                       €100
**Data validation**
Matching and validation for writers, artists and albums   €750
Duplicate work identification, adding, updating or error  €250
Error reporting view                                      €100
**Data import**
Importing writers, artists and albums                     €250
Importing works and recordings                            €250
**Quality assurance, documentation and release**
Integration tests                                         €300
Documentation update                                      €100
Minor release                                             €50
**Total**                                                 **€2250**
========================================================= =========

MWN (DDEX)
----------

This is about finding a sponsor who would be willing to be a guinea pig. If you would like to be both, please contact the maintainer.

Recording-related data and other DDEX formats
---------------------------------------------

All these features would be a great addition, however, it really comes down to the use case someone has in mind. Please contact the maintainer if you would be interested in sponsoring any development of this nature.

Requested Features under consideration
######################################


CWR Delivery service
--------------------

This is definitelly something that would be very helpful. There are three issues here:

* every society and/or administrative agency uses a slightly different delivery system
* this requires some kind of background worker or at least a cron job, so it is a bit more complicated to deploy
* we are deailing with sensitive data here, bad deployments might easily result in security issues, data loss or worse.

Definitelly something to look into. Maybe as a separate package?
