Frequently Asked Questions
==========================


Important Questions
+++++++++++++++++++

Should I read the documentation? Which parts?
	Yes. All of it.

Should I read the documentation before reading FAQ?
	Yes. All of it.

Should I read the documentation and the FAQ before asking for support?
	Yes. ALL of it.

Can I search through the documentation?
	Yes. Please do.


Django Music Publisher is not
+++++++++++++++++++++++++++++

Django Music Publisher is an open source software for original music publishers.

Is it for administrators (who may or may not also be original publishers)?
	No.

Is it for sub-publishers (who may or may not also be original publishers)?
	No.

Is it for unpublished writers?
	No.

Is it a used to create music?
	No.

Is it used for music notation?
	No. 

Can it be used to stream music?
	No.

Is it a music library?
	No.

Made by aliens (ancient or not)?
	No.


What is ...?
++++++++++++

What is a music publisher?
	See `Wikipedia <https://en.wikipedia.org/wiki/Music_publisher_(popular_music)>`_.

What is an **original** music publisher?
	Original publisher is a publisher who is signing publishing agreements with composers and lyricists. It is a **publisher role**, not a type of publisher.

What other kinds are there?
	Publishers also can sign agreements with other publishers. The most important roles are **administrator** and **sub-publisher**.

What is the difference between original publishers, administrators and sub-publishers?
	That would be beyond the scope of this document. What is important is that both require significantly more complex data structure and therefore also a far more complex user interface. Django Music Publisher does not support anything beyond the role of original publisher.

What is Common Works Registration (CWR)?
	CWR is a specification of a process and a file format for registering musical works with collecting societies worldwide.

What is ``relative share`` exactly?
	When writers (composers and lyricists) create a work, they split the shares among them. This is ``relative share``. A writer may then have a publisher, which would be you in this case. They usually transfer 50% of performance and 100% of mechanical and synchronization rights to the publisher. If this is not the case, then Django Music Publisher is not the tool for you.

What is ``publisher fee`` exactly?
	This field is **not used for registrations**. In some cases the publisher has to pay part of their revenues to the writer. The **kept** percentage of it is referred to as ``publisher fee``.

Does ``publisher fee`` apply to performance, as well as to mechanical and syncronization royalties?
	This depends on options selected during the import of processing statements.


Does it ...?
+++++++++++++++

Export Common Works Registration (CWR) files and process acknowledgements?
	Yes.

Export Electronic Batch Registration (EBR) files?
	No. EBR is officially accepted by MusicMark (ASCAP, BMI, SOCAN) and 
	unofficially also by a few other societies. All of them also accept CWR.

Export MWN (DDEX) or any other DDEX format?
	No. MWN is on the roadmap, you are welcome to sponsor the development (See :doc:`Sponsored Features <features>`). Other 
	DDEX formats may follow.

Export some other format specified by someone?
	No. There are, actually, two JSON-based export formats. They are created by the maintainer of this project and used in several projects, but it is work in progress, and is still unspecified.

Import CWR acknowledgements?
	Yes. However, if it contains additional information, thet one needs to use an external tool. The maintainer has two freely available:

	* `ACK Tools <https://matijakolaric.com/free/cwr-x-ack-tool/>`_	
	* `Visual CWR <https://matijakolaric.com/free/cwr-syntax-highlighter/>`_	

Import metadata from other sources?
	Formats used by Django's ``loaddata`` are, naturally, supported, but nothing else at the moment. Importing data is important and is on the roadmap. You are welcome to sponsor the development (See :doc:`Sponsored Features <features>`).


Various Questions
++++++++++++++++++++++++++++++++

My work has several recording versions. How do I put it in?
	Django Music Publisher only supports a single (first) recording per work.
	This also means that one ISWC can only have one ISRC assigned to it.
	In many cases, it is eanough to use ``Alternate Titles``. However, if ISRC or some other data is required for additional rerordings, then Django Music Publisher is not the right solution for you. 

Where do I put the duration of the composition?
	Compositions do not really have a duration, recordings do. So, it is only possible to assign duration to the ``First Recording``.

I dont have ISWC codes. What do I do?
	You can enter other data and then add ISWCs later on. You should ask your society how to apply. Some will assing them automatically once you register by CWR. If that is the case, then you will be able to import them from acknowledgement files.

Is there any way of auto-filling the works?
	There is a simple way to add similar works. Open a work that you want to use as a template, enter the changes and then press on ``Save as new``. The new work will be saved and opened. Repeat for all works.
