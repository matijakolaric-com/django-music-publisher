Future Releases
###############

Upcoming release schedule
++++++++++++++++++++++++++++++++++++++++++++++++++

Current plan is to have two releases in 2019, one in 2020 and then one every two years, with Django LTS releases. This is due to the fact that CWR 3.0 is going to be released soon, as well as new DDEX versions. Also, MLC may come up with a new set of requirements in the next year, but once all of that is done, we will most likely return to the slow progress of the industry.

=======  ====================================================================================================  ==========  ==========  ==========
Upcoming Major Releases                                                                                                Release dates for
-------------------------------------------------------------------------------------------------------------  ----------------------------------
version  short description                                                                                     beta        release c.  stable 
=======  ====================================================================================================  ==========  ==========  ==========
18.11\*  CWR 3.0 WRK (work registration) compatibility; New documentation                                      27.11.2018  04.12.2018  07.12.2018
19.2     CWR 3.0: ISWC handling, licence reporting; Sponsored features                                         12.02.2019  18.02.2019  22.02.2019
19.7                                                                                                           05.07.2019                        
20.3                                                                                                           31.01.2020                        
21.4                         
=======  ====================================================================================================  ==========  ==========  ==========

\* Version 18.11 will be delayed, avaiting a bugfix Django 2.1.4 release

Compatibility
+++++++++++++++++++++++++++++++++++++++++++++++++

The goal is to support only Django LTS versions, as well as only Python 3 versions that come with supported Ubuntu LTS versions, including the pre-releases.

It is tested with SQLite3 and PostgreSQL, when it comes to PostgreSQL, it is tested against the oldest supported releases.

=======================  ============  =============  ==========
Django Music Publisher   Django        Python         PostgreSQL
18.11                    2.0\*, 2.1    3.5, 3.6, 3.7  9.4 to 9.6
19.2                     2.1, 2.2 LTS  3.5, 3.6, 3.7
19.7                     2.2 LTS       3.6, 3.7
20.3                     2.2 LTS
21.4                     3.2 LTS
=======================  ============  =============  ==========

\* Depends if the 2.0.10 version will be released with 2.1.4, if not, the support will be dropped.
