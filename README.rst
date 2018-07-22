Django Music Publisher
*******************************************************************************

This is a simple **Django app for original music publishers**. The app is 
released under `MIT license <LICENSE>`_ and is basically free. However, it uses
a paid external service for data validation, creation of CWR files and parsing 
of CWR acknowledgement files, so using it is *not free*. Free 15-day demo 
licence for this service is available upon request. Please start 
`here <https://matijakolaric.com/development/cwr-toolset/#demo-and-tool-preview>`_.

It covers just a single use-case:
**one original publisher**, publishing **original musical works**.
(Original work is one that is not a modification of existing work.)
Situations with multiple writers are covered, but other publishers are ignored.
This still results in correct CWR files.

If you want to use it for exactly this purpose, just follow the standalone 
deployment instructions below. 

If you are looking for a solution that covers much more territory, this may be 
an educational proof of concept, maybe even a good starting point for a
custom development. It has very little dependecies and each model has an 
abstract parent, so including it in your project, even an existing one, should

`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_
covers basically all cases of CWR generation, validation and parsing. It is 
being constantly tested with most collecting societies and major publishers.

django-music-publisher
