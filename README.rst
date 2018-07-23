Django Music Publisher
*******************************************************************************

**NOT READY FOR DEPLOYMENT**

This is a simple **Django app for original music publishers**. The app is 
released under `MIT license <LICENSE>`_ and is basically free. However, it uses
a paid external service for data validation and creation of CWR files, so using
it is *not free*. Free 15-day demo licence for this service is available upon 
request. 

Introduction for Music Publishers
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are not a software developer, looking for a software solution for music
publishers, then everything beyond this point may be too technical for you.

This is a code repository. You may install this code on your computer or server
and use, but it is not intended to be simple. It is intended to be customizable
and extendable.

Introduction for Software Developers
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are looking for an open source code to make a custom software for a 
client who is a music publisher, and particularily if it includes Common Works
Registration (CWR) or even Electronic Batch Registration (EBR), and you have
never worked in this industry before, then you need to learn that things in 
this industry are purposfully made extremely complicated. For large publishers,
complicated is financially much better than complex. And money talks.

Use Case
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This app covers just a single use-case:
**one original publisher**, publishing **original musical works**.
(Original work is one that is not a modification of existing work.)
Situations with multiple writers are covered, but other publishers are ignored.
This still results in correct CWR files and enough data to acquire ISWC.

If you want to use it for exactly this purpose, just follow the standalone 
deployment instructions below.

Beyond
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you are looking for a solution that covers much more territory, this may be 
an educational proof of concept, maybe even a good starting point for a custom 
development. It has very little dependecies and each model has an abstract 
parent, so including it in your project, even an existing one, should be pretty 
straightforward.

On the other hand, required data structure for a general publishing software is 
far more complex, even the part dealing with registrations. Everybody falls the
first time in designing the data structure, unless they have help. Yes, this is
a sales pitch.

CWR Developer Toolset
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

`CWR Developer Toolset <https://matijakolaric.com/development/cwr-toolset/>`_
covers basically all cases of CWR generation, validation and parsing. It is 
being constantly tested with most collecting societies and major publishers. 
There are various licencing packages.

This particular software uses two of the tools, one for data validation and one
for generation of CWR files. It will work without the licence, but data will
not be validated as CWR-compliant, and there will be no way to create CWR.

