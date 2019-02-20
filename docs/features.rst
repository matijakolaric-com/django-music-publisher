Sponsored Features
##################

Django Music Publisher is free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell. It can only be developed further with the help of sponsors.

Version |version| was sponsored by `DMP Guru <https://dmp.guru>`_, a specialized platform-as-a-service provider for Django Music Publisher instances. You can have your own DMP instance set up and running in a minute. First 30 days are free.

Features added in this release (including minor releases)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Here are development cost breakdowns for several features that have been identified as previously missing, which have been added in this major release.

======================================================= =========
Task                                                    Cost
======================================================= =========
Work model changes, new writer capacities                  €250
Validation rules spanning NWR/REV, VER, SWR, OWR rows      €250
CWR validation in DMP                                      €500
CWR generation in DMP                                     €1000
Royalty distribution processing (features implemented)     €750
Integration tests                                          €500
Documentation update                                       €250
Major release                                              €100
**Total**                                               **€3600**
======================================================= =========

The following features were added in minor releases.

======================================================= =========
Task                                                    Cost
======================================================= =========
Alternate titles as suffixes                               €200
CWR internal note                                           €50
New filters for Work                                        €50
Integration tests                                           €50
Documentation update                                        €50
**Total**                                                **€400**
======================================================= =========

Previous releases of Django Music Publisher used an external service for data validation, CWR generation and syntax highlighting. Django Music Publisher began as a proof of concept for this service. However, data validation and CWR generation are the most important features of Django Music Publisher.

Previous releases of Django Music Publisher had some limitations, inherited from the external CWR generation service it used. One such limitation was that it only allowed registration of original musical works, not modifications.

Also, the core royalty distribution has been implemented, please see next section for details.

Features still missing
++++++++++++++++++++++

Royalty Distribution Processing
-------------------------------

There are many different input formats, and they also come in different currencies with different conversion rates at different dates. However, much of the work can be done in Excel, once the basic distribution has been calculated.

The processing core has been added, but there is still a lot to do.

========================================================= =========
Task                                                      Cost
========================================================= =========
Royalty distribution processing (features implemented)    €750
Creating a custom exporting template                      €250
Integrating exports into custom template                  €250
Creating Common Royalty Distribution import               €500
Creating a custom import (per spreadsheet format)         €150
Documentation update                                      €250
Minor release                                             €100
**Subtotal**                                              **€2250**
Already sponsored by DMP Guru and implemented in 19.1     -€750
**Total**                                                 **€1500**
========================================================= =========

Please note that this feature will be a sub-project with a separate repository.

Data import
-----------

Current releases do not support data imports from third party software solutions or spreadsheet data. So far the maintainer has been providing this as a paid service. However, it would be in public interest if people would be able to do it themselves.

There are several caveats here, the first one is related to internal work numbering. If imported data was already used for registrations via CWR or EBR or any format that has submitter work IDs, then they must be maintained. However, Django Music Publisher creates it's own work IDs and adding custom ones will create several new potential issues.

Second one is that usual formats often contain more data then Django Music Publisher can hold, but it is not possible to calculate the shares back to initial distribution among writers.

The third issue is that often the input file does not contain all the data required for a minimal CWR, so the data can not pass the validation.

As long as data is imported from a custom spreadsheet or JSON format that does not have work IDs, the responsibility for these issues is not with the software. Within these boundaries, the cost estimates are:

========================================================= =========
Task                                                      Cost
========================================================= =========
Creating custom a spreadsheet template                    €200
Creating import model and interface                       €200
**Data validation**
Matching and validation for writers, artists and albums   €500
Duplicate work identification, adding, updating or error  €300
Error reporting view                                      €100
**Data import**
Importing writers, artists and albums                     €250
Importing works and recordings                            €250
**Quality assurance, documentation and release**
Integration tests                                         €300
Documentation update                                      €100
Major release                                             €100
**Total**                                                 **€2300**
========================================================= =========

MWN (DDEX)
----------

MWN is a format that has similar data structure to CWR, though the underlying format is completely different. It requires a licence to be used, from which it is quite unclear whether it is legally possible to integrate the functionality into an open source solution.

Implementing it is definitely cheaper than paying for a legal interpretation.

Recording-related data and other DDEX formats
---------------------------------------------

Same thing.


CWR Delivery service
--------------------

This is definitely something that would be very helpful. There are three issues here:

* every society and/or administrative agency uses a slightly different delivery system
* this requires some kind of background worker or at least a cron job, so it is a bit more complicated to deploy
* we are dealing with sensitive data here, bad deployments might easily result in security issues, data loss or worse.

The solution exists, but it is not going into the open source code in the foreseeable future.

Multiple Recordings per Work
----------------------------

When CWR 3.0 specification is released, details will be released.