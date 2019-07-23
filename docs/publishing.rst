Brief Overview of Music Publishing
#########################################

This is a very brief introduction for software developers and system administrators. It is required as music rights are quite complex and often counter-intuitive and available information can be misleading.

Music Publishing
****************

Music publishing started with publishing of sheet music, and first music *performing* rights societies were formed in the mid-1800s, predating recording, telephone and radio. With the invention of recording techniques, *mechanical* rights became a thing and some societies decided to cover them as well, while in some countries, new organizations were formed. All of them are called collecting organizations, but in official CWR documentation, they are referred to as *societies*. The third type are *synchronization* rights, basically music used for advertising.

Although sheet music is not in the focus any more, *composers and lyricists (writers)* still have contracts with *music publishers*. When a (co-)writer has a contract about a musical work with a publisher, this publisher is original publisher of the work in question. Usually 50% of performing and 100% of mechanical and synchronization rights are transferred to the original publishers. Each writer can have a different publisher, or even multiple ones, or not have one at all.

Writers and publishers who are in the chain of agreements that includes the sender of the CWR file are referred to as *controlled*.

Please note that *musical work means composition and lyrics*, this has nothing to do with sound.

Each original publisher has a fiduciary obligation to register client’s shares, when they register their own at collecting organizations they are affiliated with.

Royalties for collecting rights are paid, based on registrations. There is a popular belief among writers that by registering in their home societies, other societies will somehow magically know about that. While some collecting organizations share data among themselves, most of them do not.

Publishing Roles
****************

In the context of registrations, basically there are three roles:

* *original publishers* (OPs) who have a direct deal with writers
* *administrators* to whom some OPs have entrusted all or some activities regarding musical works
* *sub-publishers* to whom OPs or admins have entrusted all or some activieties in foreign countries

Django Music Publisher covers the need of publishers who are only performing the role of an original publisher. Furthermore, it does not cover the case of composite works and some other rare cases.

Please note that the term *self-publisher* is used for an original publisher with a single signed writer - usually the owner, or sometimes all members of a band. They usually do not require royalty statement processing.

Publisher Size
**************

In the software context, the size of a publisher is completely irrelevant. There are self-proclaimed small music publishers who do just about everything and anything, as well as large publishers who are just original publishers or just administrators or just sub-publishers.

In the context of Django Music Publisher, original publishers with up to about 1000 works (depending on metadata complexity), effectively self-publishers, will fit within the free tier of Heroku, limited to 10.000 database rows.
