Sponsored Features
##################

Here are development cost breakdowns for several features that have been identified as missing in previous releases.

Free CWR
----------------------

Previous releases of Django Music Publisher used an external service for data validation, CWR generation and syntax highlighting. Django Music Publisher began as a proof of concept for this service. 

However, data validation and CWR generation are the most important features of Django Music Publisher and they belong into the open source code. Here is what needs to be done:

=================================================== =========
Task                                                Cost
=================================================== =========
CWR validation in DMP (with current features)       €500
CWR generation in DMP (with current features)       €1000
Integration tests                                   €300
Documentation update                                €100
Minor release                                       €50
**Total**                                           **€1950**
=================================================== =========

Please note that these changes **do not include CWR syntax highlighting**, which is a very nice thing to have, but not really a crucial one. 


Modifications of existing works
-------------------------------

Previous releases of Django Music Publisher had some limitations, inherited from the external CWR generation service it used. One such limitation is that it only allows registration of original musical works, not modifications.

Once the previous feature was finished, i became possible to remove this limitation. Here is what needs to be done:

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


Royalty Distribution Processing
-------------------------------

There are many different input formats, and they also come in different currencies with different conversion rates at different dates. However, much of the work can be done in Excel, once the basic distribution has been calculated.

This is cost breakdown for a simple case (ASCAP/BMI/SOCAN).

========================================================= =========
Task                                                      Cost
========================================================= =========
Creating an output spreadsheet template                   €100
Creating a basic parsing / exporting framework            €750
Creating a custom import (per spreadsheet format)         €150+
Documentation update                                      €100
Minor release                                             €50
**Total**                                                 **€1150+**
========================================================= =========


Data import
-----------

Current releases do not support data imports from third party software solutions or spreadsheet data. So far the maintanier has been providing this as a paid service. However, it would be in public interest if people would be able to do it themselves.

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

The following features are required in order to make Django Music Publisher completely free and available to small music publishers without any limitations:

* Adding MWN (DDEX)
* Extending the features towards the recording/label side of music rights
* Implementing other DDEX formats/processes
* Automated CWR delivery (first to MusicMark and ICE Services)