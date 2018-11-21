Upcoming release schedule
++++++++++++++++++++++++++++++++++++++++++++++++++

Django Music Publisher uses the Fibonacci Release Cycle, with a monthly unit. This coincides with updates of specs, DDEX was just updated, CWR is just about to be, MLC will be defined in 2019 and will go into effect early in 2020. On the other hand, the scope of the project is pretty narrow, without any plans to make it broader, and the industry is otherwise evolving slowly, so there will likely be very few new feature requests. Most likely, new major versions will only be coming out with new LTS releases of Django.

The goal of this project is not to compete with commercial solutions, but to lead the way with *light versions* of new features. If you disagree, feel free to fork this project.

=======  ====================================================================================================  ==========  ==========  ==========
Upcoming Major Releases                                                                                                Release dates for
-------------------------------------------------------------------------------------------------------------  ----------------------------------
version  short description                                                                                     beta        release c.  stable 
=======  ====================================================================================================  ==========  ==========  ==========
18.11\*  CWR 3.0 WRK (work registration) compatibility; Royalty statement processing foundation                27.11.2018  04.12.2018  07.12.2018
19.2     CWR 3.0: ISWC handling, licence reporting, DDEX: MWN                                                  12.02.2019  18.02.2019  22.02.2019
19.7     multiple recordings per work; Neigbouring rights, DDEX: RIN; YT, FB                                   05.07.2019                        
20.3     MLC-related changes                                                                                   31.01.2020                        
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
19.2                     2.1, 2.2LTS   3.5, 3.6, 3.7
19.7                     2.2LTS        3.6, 3.7
20.3                     2.2LTS        3.6, 3.7 
21.4                     2.2 & 3.2LTS  3.6, 3.7 
=======================  ============  =============  ==========

\* Depends if the 2.0.10 version will be released with 2.1.4, if not, the support will be dropped.
