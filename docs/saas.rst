Software as a Service
#####################

The idea behind Django Music Publisher was to give small publishers an opportunity to compete. The current version, extended with the CWR generation code or together with the existing CWR service the maintainer provides, is up to the task. However, the deployment and technical maitenance may still be too complicated for an average small publisher.

The code is released under MIT licence, which allows anyone to provide a commercial or a free service based on it, potentially with some extensions. Some general guidelines along these lines are provided in this section. The technical part requires an experienced Django developer, but most of it should be generally understandable.

Who could do it and why
-----------------------

Soocieties (PROs, MROs) or Administrative Agencies
==================================================

In an ideal world, societies would provide such a service for free. Most of them already provide some of this functionality through their web interfaces, but not nearly all of them. Also, their existing services are dead ends, as any custom integration or extension is not possible. While this ensured some kind of lock-in for their affiliates, today the societies are competing.

Providing Django Music Publisher, optionally customized and branded, to their affiliates for free or at cost would greatly benefit both them and their affiliates. The main benefit for the societies is a very simple one: less user support. It offers superb data validation as users enter their data, so there would be far less user support due to errors. They can simply skip the whole initial testing. And if delivery gets automated, maybe even directly, bypassing the CWR, it would decrease the need for user support even further.

Surely, supporting the affiliates in using it does need additional user support, but the benefits should be significant. They would be offering more for less. The cost of installing and maintaining such a system is insignificant compared to to the reduced costs of affiliate support.

The benefit to the affiliates is also quite obvious. They have a simple and workable solution with no or little additional costs. Being open source, it can not really become a dead end, they can always export their data and move to a commercial service (covered next) with additional features, or host the same solution themselves and extend and/or integrate it as needed.


Majors - Administrators and Sub-Publishers
==========================================

The advantage should be pretty obvious. Original Publishers have a series of choices what to do themselves and what to delegate to administrators and/or sub-publishers. Integrating one-click administration or sub-publishing agreements is a relatively simple custom extension.

Commercial Services
===================

One takes the code, wraps it in a SaaS, maybe adds few additional features and charges for it. There surely is a business model in there. And eventually, one can move to administration and/or sub-publishing.


Techical issues
---------------

Providing Custom Settings
=========================

The first and foremost question is how to provide custom settings for each of the clients. Most of the settings can be set through environment variables with the existing code, but not the definition of the publisher entity (or entities for the US). There are severaal good ways to do it, and there isn't a generally best option. Setting it through a JSON-encoded setting is the simplest solution.

Database and Upgrades
=====================

Django Music Publisher does not support multi-tenant database schema. Multiple schemas are certainly possible, but that is almost the same as multiple databases. One definitelly has to provide automated migrations for all clients, but this only requires a simple script.

However, creating a multi-tennant schema solution should be a straightforward procedure for an experienced Django developer. It has been done by the maintainer and all the prerequisits are there.

Containers
==========

Using containers is the way to go in most cases. 

Central Application
===================

There are no presumptions about the central application, used for client registration, general management and billing. One can definitelly start small, doing a lot of things manually, with services like Heroku and/or AWS and grow, or extend an existing application for client/affiliate management.

