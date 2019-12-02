Introduction
=================================

Django-Music-Publisher is open source software for original **music publishers**. It is based on `Django web framework <https://www.djangoproject.com/>`_, hence the name.

Django-Music-Publisher is a tool for **managing metadata** for musical works and recordings. It has basic support for **royalty distribution processing** and uses `Common Works Registration (CWR) <https://matijakolaric.com/articles/1/>`_ for **batch registrations of musical works** with `collecting societies <https://en.wikipedia.org/wiki/Copyright_collective>`_.

Project Scope
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django-Music-Publisher can be used out-of-the-box by most small publishers, both in commercial and production music. Others can use it as a proof of concept or as a base for custom development.

Each Django-Music-Publisher instance supports a **single original publisher**. It is not intended to be used by administrators or sub-publishers, nor by publishing companies with multiple entities.


Features
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The database contains data on **musical works** and **recordings**, including titles of **original works** for **modified works**, **alternative titles**, data on **writers**, recording and performing **artists**, **releases** (albums) and **music libraries**, as well as **CWR exports**, **registration acknowledgements** and **ISWC assignments**.

Multiple writers, both controlled and uncontrolled, are covered, with minor limitations.

Basic original publishing agreement data can be entered, sufficient for registrations in societies that require society-assigned agreement numbers and for simple royalty distribution processing.

The actual royalty distribution processing is not yet implemented.


Limitations
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django-Music-Publisher is aiming to be a simple tool that is good enough for most original publishers. Being simple means that there are some limitations.

It does not manage data on "other" publishers. Co-publishing deals are still possible, with each publisher registering their own shares.

With default settings, it is presumed that **controlled writers** collect 50% of performing rights and the other 50%, as well as 100% of mechanical and sync are collected by the **original publisher (you)**.
Currently, this can not be changed through settings.

Recordings based on multiple musical works (e.g. medleys) are not supported.

When creating CWR, many fields are left with blank/zero values. When the fields are required in CWR, it uses reasonable defaults, e.g.:

* Musical Work Distribution is set to Unclassified
* Recorded indicator is set to Unknown if no recording has been entered and to Yes if it has been entered
* Grand Rights Indicator is set to No
* Reversionary Indicator is set to No
* First Recording Refusal Indicator is set to No
* Work for Hire is set to No

If this is not how you work, then this is not the tool for you, but you are free to extend it for your needs.


Deployment options
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Django-Music-Publisher, as any Django-based application, can be installed in
many different ways.

`Heroku <heroku.com>`_ is a well-known cloud platform, offering a very simple
installation procedure for cloud-native applications. The free tier is enough
for publishers with up to ~1000 musical works. Also, this is the fastest way
to test Django-Music-Publisher.

Other ways include:

* installed on a local computer (not recommended for real work)
* custom VPS installation (requires basic sysadmin skills)
* to be included in a larger Django project (requires significant coding skills)

