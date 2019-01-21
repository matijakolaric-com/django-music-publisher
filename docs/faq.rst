Frequently Asked Questions
==========================


Important Questions
+++++++++++++++++++

Should I read the documentation? Which parts?
	Yes. All of it.

Should I read the documentation before reading FAQ?
	Yes. All of it.

Should I read the documentation and the FAQ before asking for support?
	Yes.

Can I search through the documentation?
	Yes.


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

What is the difference?
	That would be beyond the scope of this document. What is important is that both require significantly more complex data structure and therefore also a far more complex user interface. Django Music Publisher does not support anything beyond the role of original publisher.

Does it ...?
+++++++++++++++

Export Common Works Registration (CWR) files and process acknowledgements?
	Yes.

Export Electronic Batch Registration (EBR) files?
	No. EBR is officially accepted bu MusicMark (ASCAP, BMI, SOCAN) and 
	unofficially also by a few other societies. All of them also accept CWR.

Export MWN (DDEX) or any other DDEX format?
	No. MWN is on the roadmap, you are welcome to sponsor the development. Other 
	DDEX formats may follow.

Export some other format specified by someone?
	No. There are, actually, two JSON-based export formats. They are created by the maintainer of this project and used in several projects, but it is work in progress, and is still unspecified.

Import?
	Formats used by Django's ``loaddata`` are, naturally, supported, but nothing else at the moment. Importing data is important and is on the roadmap. You are welcome to sponsor the development.

