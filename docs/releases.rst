Release Policy
##############

Major versions of DMP are released in January and July. Minor versions,
containing bug fixes and/or security updates are released as required.

Past versions with new features
===============================

18.7 - 18.11
------------

Initial release in July 2018 had a very simple data structure. It used external API
for CWR generation. The code was open-source, but it was dependant on a free tier of a commercial service.

19.1 Epiphany
-------------

CWR generation and complete data validation was added to the open-source code. Full support for
modified works was added, as well as basic co-publishing support.
Data export in JSON format was added.

19.7 Metanoia
-------------

Support for multiple recordings per work and CWR 3.0 generation, labeled as "experimental", were added.
CWR preview, for both versions, received basic syntax highlighting. Since this version, CWR files are zipped.

20 Twenty
---------

Twenty-twenty was primarily about simplified deployment. Since this version, DMP can be deployed to the Free Heroku dyno
(container) by non-techies.

Support for custom global share splits was added. MR/SR affiliations for writers are available when implied by share
split settings.

Syntax highlighting for CWR acknowledgements was added, for simpler dealing with conflicts and other registration-related
issues.

20.7 Endemic
------------

Index (home) page became clearer due to grouping of views.

Basic CSV imports and exports for musical works, and JSON exports of releases were added.

Controlled writers with no society affiliation are now fully supported.

Future open-source features
===========================

DDEX
----

DDEX is a set of standards for music metadata exchange. Sadly, their licence is not compatible
with open-source licences. If it ever becomes compatible with MIT License, support for it will
be added to the open-source code.

.. note::

    See `Beyond DMP <https://matijakolaric.com/articles/2/beyond/>`_ for commercial options.


Royalty processing for music publishers
---------------------------------------

When it comes to music publishing, the royalty processing is the only unfinished area.
The main challenge here is that incoming statements come in many different formats.
Processing of the most common ones will be added to open-source code.

.. note::

    See `Beyond DMP <https://matijakolaric.com/articles/2/beyond/>`_ for commercial options.

Support for small music labels
------------------------------

It took just over two years to come to the point where most needs of most small publishers
are covered. From late 2020, focus will shift toward supporting small labels.

Any feature that is fully sponsored
-----------------------------------

If you believe that a feature should be available as open-source code, feel free to pay for
the development.

Closed-source features
=========================================================

There is a business model behind Django-Music-Publisher. In order for a feature to be
released as open-source code, all or most of the following must apply:

* Code must be global, or near-global. Special cases that apply to just one or a small
  number of countries are not covered in open-source, unless fully sponsored.
  E.g. US publishers with multiple affiliations and BUMA/STEMRA
  share split rules are not covered.

* Code must be applicable to small publishers (and soon labels). The goal is to help them
  grow. If a feature is required only by established companies, it will not come into
  open-source, unless fully sponsored. E.g. administrators and sub-publishers.

* A feature must not require customisations or complex deployments.
  Open source solutions for end-users make no sense if a professional is required to
  deploy and/or customise it.
  E.g. registrations in GEMA and licencing of production music are not supported

* A feature should be self-evident to experienced professionals, so no user support is
  required. This is not an absolute rule, the author and maintainer runs a
  `professional support service <https://matijakolaric.com/dmp-prosupport/>`_.
  Some confusing features were removed in the past, e.g. two JSON formats.

* It must be legal. E.g. integrating DDEX into open source is currently not.

.. note::

    All of the aforementioned examples are available in DMP's commercial extensions,
    sibling and another solution.
    See `Beyond DMP <https://matijakolaric.com/articles/2/beyond/>`_.
