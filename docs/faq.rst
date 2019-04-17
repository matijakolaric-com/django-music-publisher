Frequently Asked Questions
==========================


Important Questions
+++++++++++++++++++

Should I read the documentation? Which parts?
	Yes. All of it.

Should I read the documentation before reading FAQ?
	Yes. At least the user manual.

Should I read the documentation and the FAQ before asking for support?
	Yes. ALL of it.

Can I search through the documentation?
	Yes. Please do.
	

Django Music Publisher is not
+++++++++++++++++++++++++++++

Django Music Publisher is an **open source software for original music
publishers**.

Is it for administrators (who may or may not also be original publishers)?
	No.

Is it for sub-publishers (who may or may not also be original publishers)?
	No.

Is it for unpublished writers?
	No.

Is it used to create music?
	No.

Is it used for music notation?
	No. 

Can it be used to stream music?
	No.

Is it a music library?
	No.

Made by aliens (ancient or contemporary)?
	No.


What is ...?
++++++++++++

What is a music publisher?
	See `Wikipedia <https://en.wikipedia.org/wiki/Music_publisher_(popular_music)>`_.

What is an **original** music publisher?
	Original publisher is a publisher who is signing publishing agreements with
	composers and lyricists. It is a **publisher role**, not a type of
	publisher.

What other kinds are there?
	Publishers also can sign agreements with other publishers. The most
	important roles are **administrator** and **sub-publisher**.

What is the difference between original publishers, administrators and
sub-publishers?
	That would be beyond the scope of this document. What is important is that
	both require significantly more complex data structure and therefore also a
	far more complex user interface. Django Music Publisher does not support
	anything beyond the role of original publisher.

What is Common Works Registration (CWR)?
	CWR is a specification of a process and a file format for registering
	musical works with collecting societies worldwide.


Open Source / Free
++++++++++++++++++

Does "free" mean "free of charge"?
	Yes. If you install if from the official repository, then you can use it free of charge. 
	But anyone is also free to sell it, so it may not be free of charge elsewhere.

What is open source?
	Open source means that the whole source for this program is freely available.

Is `DMP Guru <https://dmp.guru>`_ charging for the use of this software?
	No. DMP Guru is a specialised application platform-as-a-service. They install, host and 
	maintain **your app instance** of Django Music Publisher and charge for this service.

Is there a difference? I am still paying for it?
	Yes, there is a difference. There is no lock-in. You can download the database backup, install 
	Django Music Publisher somewhere else, import the database data, and keep using it. There will
	be no significant differences. You are paying for the convenience.

Are there other services that use Django Music Publisher in some way?
	Yes. None has so far chosen to advertise this fact, and the maintainer respects this choice, so they will not be named here.


Who is ...?
+++++++++++

When my society says I should ask the vendor about some issue, who do I ask?
	Regardless if you installed Django Music Publisher yourself, or are using
	DMP Guru, the software vendor in their meaning of the word is **you**,
	as you have accepted the MIT licence, which makes clear that the software
	comes 'as is'.

	Having said that, you are welcome to report any potential bugs to the
	repository. The maintainer may choose to help you. Or not.

	DMP Guru provides support for their service, but issues raised by societies
	have nothing to do with hosting and maintenance, but they will report the
	bug to the maintainer if there is a bug.


Does it ...?
+++++++++++++++

Export Common Works Registration (CWR) files and process acknowledgements?
	Yes.

Export Electronic Batch Registration (EBR) files?
	No. EBR is officially accepted by MusicMark (ASCAP, BMI, SOCAN) and 
	unofficially also by a few other societies. All of them also accept CWR.

Export MWN (DDEX) or any other DDEX format?
	No. MWN is on the roadmap, you are welcome to sponsor the development
	(See :doc:`Sponsored Features <features>`). Other DDEX formats may follow.

Export some other format specified by someone?
	No. There are, actually, two JSON-based export formats. They are created by
	the maintainer of this project and used in several projects, but it is work
	in progress, and is still unspecified.

Import CWR acknowledgements?
	Yes. However, if it contains additional information, then you must use an
	external tool. The maintainer has two freely available:

	* `ACK Tools <https://matijakolaric.com/free/cwr-x-ack-tool/>`_	
	* `Visual CWR <https://matijakolaric.com/free/cwr-syntax-highlighter/>`_	

Import metadata from other sources?
	Formats used by Django's ``loaddata`` are, naturally, supported, but
	nothing else at the moment. (If you dont understand, it means **No** in
	Geek.) Importing data is important and is on the roadmap. You are welcome
	to sponsor the development (See :doc:`Sponsored Features <features>`).


Which societies...?
+++++++++++++++++++

Every society (CMO, PRO, MRO, etc.) is somewhat different. Django Music
Publisher has been tested with some of them, and other software solutions by
the maintainer have also been used in many more. Here is what we know.

PRS/MCPS
	Registering and acknowledgement processing works flawlessly. For new works,
	ISWCs are issued **after** the successful registration. One has to request
	it as CSV from PRS/MCPS and import. Manually adding ISWCs is also possible.

BUMA/STEMRA, GEMA, SABAM, KODA, STIM, TEOSTO, TONO
	Registering and acknowledgement processing works flawlessly (same as in
	PRS/MCPS). ISWC imports have not yet been tested.

SACEM, SIAE, ZAIKS, SGAE, SPA, SUISA
	Works, but not everything was tested so far, as users did not use all
	features of Django Music Publisher. No issues are expected.

APRA, AKM/AUME, MUSICAUTOR, OSA, IMRO, UCMR-ADA, ACUM
    Other registration software by maintainer works there without issues, no
    issues are expected, but not tested yet.

ASCAP, BMI, SESAC/HFA, SOCAN/SODRAC, CMMRA
    Django Music Publisher and other registration software by maintainer works.
    Lately there were some issues due to software changes in SESAC/HFA and it
    is not clear to the maintainer how Musicmark will process SODRAC (SOCAN RR)
    registrations. With Django Music Publisher, no issues are expected.

    Please note that US mode with enities in all US PROs is not publicly
    available in DMP Guru.

SAMRO, MESAM
	Requires more testing, probably completely compatible.

Other EU Societies
	In most, nothing was tested. In some, acknowledgement files are very messed
	up and can not be imported. Some do not send acknowledgement files at all,
	or just send acknowledgement files for the first part od the two-part
	registration process.

Europe, not in EU
	Absolutely no idea.

Asia (except ACUM and MESAM) and Africa (except SAMRO)
	Absolutely no idea.

Latin America
	It's complicated.


Various Questions
++++++++++++++++++++++++++++++++

What is ``relative share`` exactly?
	When writers (composers and lyricists) create a work, they split the shares
	among them. This is ``relative share``. A writer may then have a publisher,
	which would be you in this case. They usually transfer 50% of performance
	and 100% of mechanical and synchronization rights to the publisher. If this
	is not the case, then Django Music Publisher is not the tool for you.

What is ``publisher fee`` exactly?
	This field is **not used for registrations**. In some cases the publisher
	has to pay part of their revenues to the writer. The **kept** percentage
	of it is referred to as ``publisher fee``.

Does ``publisher fee`` apply to performance, as well as to mechanical and
syncronization royalties?
	This depends on options selected during the import of royalty statements.

My work has several recording versions. How do I put it in?
	Django Music Publisher only supports a single (first) recording per work.
	This also means that one ISWC can only have one ISRC assigned to it.
	In many cases, it is eanough to use ``Alternate Titles``. However, if ISRC
	or some other data is required for additional rerordings, then Django Music
	Publisher is not the right solution for you. Yet.

Where do I put the duration of the composition?
	Compositions do not really have a duration, recordings do. So, it is only
	possible to assign duration to the ``First Recording``.

I dont have ISWC codes. What do I do?
	You can enter other data and then add ISWCs later on. You should ask your
	society how to apply. Some will assing them automatically once you register
	by CWR. If that is the case, then you may be able to import them from
	acknowledgement files.

Is there any way of auto-filling the works?
	There is a simple way to add similar works. Open a work that you want to
	use as a template, enter the changes and then press on ``Save as new``.
	The new work will be saved and opened. Repeat for all works.
	See :doc:`Adding, Changing and Deleting Musical Works <manual_works>` for
	details.

How do I enter multiple original publishers per one writer?
	This is described
	in :doc:`Adding, Changing and Deleting Musical Works <manual_works>`.
