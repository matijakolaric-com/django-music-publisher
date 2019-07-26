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
	musical works, and several related tasks, with collecting societies worldwide.


Open Source / Free
++++++++++++++++++

Does "free" mean "free of charge"?
	Yes. If you install if from the official repository, then you can use it free of charge. 
	But anyone is also free to sell it, so it may not be free of charge elsewhere.

What is open source?
	Open source means that the whole source for this program is freely available.

Who is ...?
+++++++++++

When my society says I should ask the vendor about some issue, who do I ask?
	Regardless if you installed Django Music Publisher yourself, the software
	vendor in their meaning of the word is **you**, as you have accepted the
	MIT licence, which makes clear that the software comes 'as is'.

	Having said that, you are welcome to report any potential bugs to the
	repository. The maintainer may choose to help you. Or not.


Does it ...?
+++++++++++++++

Export Common Works Registration (CWR) files and process acknowledgements?
	Yes. CWR 2.1 is supported and well tested, CWR 2.2 will not be implemented.
	CWR 3.0 is experimental and available as a separate module.

Export Electronic Batch Registration (EBR) files?
	No. EBR is officially accepted by MusicMark (ASCAP, BMI, SOCAN) and 
	unofficially also by a few other societies. All of them also accept CWR.

Export MWN (DDEX) or any other DDEX format?
	DDEX licence is not compatible with MIT licence. DDEX promised to solve the issue promptly. Months ago.

Export some other format specified by someone?
	There are two JSON-based export formats. They are work in progress,
	and are still unspecified. However, any developer should be able to
	fiure them out.

Import CWR acknowledgements?
	Yes. However, if it contains additional information, then you must use an
	external tool. The maintainer has two freely available:

	* `ACK Tools <https://matijakolaric.com/free/cwr-x-ack-tool/>`_	
	* `Visual CWR <https://matijakolaric.com/free/cwr-syntax-highlighter/>`_	

Import metadata from other sources?
	Formats used by Django's ``loaddata`` are, naturally, supported, but
	nothing else at the moment. (If you dont understand, it means **No** in
	Geek.)


Which societies...?
+++++++++++++++++++

Every society (CMO, PRO, MRO, etc.) is somewhat different. Django Music
Publisher has been tested with some of them, and other software solutions by
the maintainer have also been used in many more. Here is what we know.

ASCAP, BMI, PRS/MCPS
	Registering and acknowledgement processing works flawlessly. For new works,
	ISWCs are issued **after** the successful registration. One has to request
	it as CSV from PRS/MCPS and import. Manually adding ISWCs is also possible.

BUMA/STEMRA, GEMA, KODA, SABAM, STIM, TEOSTO, TONO
	Registering and acknowledgement processing works flawlessly (same as in
	PRS/MCPS). There may be some country-specific rules that are not covered.

SESAC/HFA, SOCAN/SODRAC, CMMRA
    There were some issues due to software changes in SESAC/HFA and it
    is not clear to the maintainer how Musicmark will process SODRAC (SOCAN RR)
    registrations. Probably works.

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
	It's complicated. Most of the stuff will work in most societies. There may
	be some country-specific rules that are not covered.



Various Questions
++++++++++++++++++++++++++++++++

What is ``relative share`` exactly?
	When writers (composers and lyricists) create a work, they split the shares
	among them. This is ``relative share``. A writer may then have a publisher,
	which would be you in this case. They usually transfer 50% of performance
	and 100% of mechanical and synchronization rights to the publisher. In some
    countries, however, different splits may be enforced by law.

What is ``publisher fee`` exactly?
	This field is **not used for registrations**. In some cases the publisher
	has to pay part of their revenues to the writer. The **kept** percentage
	of it is referred to as ``publisher fee``.

Where do I put the duration of the composition?
	Compositions do not really have a duration, recordings do. So, it is only
	possible to assign duration to the ``Recording``.

I don't have ISWC codes. What do I do?
	You can enter other data and then add ISWCs later on. You should ask your
	society how to apply. Some will assing them automatically once you register
	by CWR.

Is there any way of auto-filling the works?
	There is a simple way to add similar works. Open a work that you want to
	use as a template, enter the changes and then press on ``Save as new``.
	The new work will be saved and opened. Repeat for all works.
	See :doc:`Works <manual_works>` for
	details.

How do I enter multiple original publishers per one writer?
	This is described
	in :doc:`Works <manual_works>`.
