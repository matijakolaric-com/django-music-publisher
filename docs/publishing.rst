Introduction for Developers and Sysadmins
#########################################

This is a very brief introduction to for software developers and system administrators, as music rights are quite complex and often counter-intuitive. It is using a techie language, publishers beware.

Music Publishing
****************

Music publishing started with publishing of sheet music, and first music *performing* rights societies were formed in the mid-1800s, predating recording, telephone and radio. With the invention of recording techniques, *mechanical* rights became a thing and some societies decided to cover them as well, while in some countries, new organizations were formed. All of them are called collecting organizations, but in official CWR documentation, they are referred to as *societies*. The third type are *synchronization* rights, basically music used for advertising.

Although sheet music is not in the focus any more, *composers and lyricists (writers)* still have contracts with *music publishers*. When a (co-)writer has a contract about a musical work with a publisher, this publisher is original publisher of the work in question. Usually 50% of performing and 100% of mechanical and synchronization rights are transferred to the original publishers. Each writer can have a different publisher, or even multiple ones, or not have one at all.

Please note that *musical work means composition and lyrics*, this has nothing to do with sound.

Writers and publishers who are in the chain of agreements that includes the sender of the CWR file are referred to as *controlled*. 

Each original publisher has, among others, a fiduciary obligation to register client’s shares, when they register their own at collecting organizations they are affiliated with.

Royalties for collecting rights are payed, based on registrations. There is a popular belief among writers that by registering in their home societies, other societies will somehow magically know about that. While some collecting organizations share data among themselves, most of them do not.

Publishing Roles
****************

In the context of registrations, basically there are three roles:

* *original publishers* (OPs) who have a direct deal with writers
* *administrators* to whom some OPs have entrusted all or some activities regarding musical works
* *sub-publishers* to whom OPs or admins have entrusted all or some activieties in foreign countries

Django Music Publisher covers the need of publishers who are only performing the role of an original publisher. Furthermore, it does not cover the case of modifications of musical works, composite works and some other rare cases.

Please note that the term *self-publisher* means original publisher with a single signed writer - usually the owner, or sometimes all members of a band.

Publisher Size
**************

In the software context, the size of a publisher is completely irrelevant. There are self-proclaimed small music publishers who do just about everything and anything, as well as large publishers who are just original publishers or just administrators or just sub-publishers.

In the context of Django Music Publisher, original publishers with up to about 1000 works, effectively self-publishers, will fit within the free tier of Heroku, limited to 10.000 database rows.

Extending Django Music Publisher
********************************

The maintainer of this project also leads a propriatery project that actually extends Django Music Publisher, and has worked on several other projects in the field in different roles.

There are generally speaking five tiers of complexity in music publishing. And they do not follow the logic publishers have. Based on years of experience:

* Tier 1 would be unpublished writers (writers with no publishers). 

* Django Music Publisher currently coveres most of the tier two. To cover the rest, support for modified works should be added, as well as some other improvements.

* Tier 3 has two sub-tiers, in the first, the uncontrolled original publishers should be added. Three more database tables in a normalized database. Then one has to add administrators, which turns one of these tables into a forest. And this is without multiple affiliations, which turns some many-to-one relations into many-to-many.

* Tier 4 includes any feature dealing with multiple territories, most notably sub-publishing.

* Tier 5 includes special features, most notably share changes across territories.

The data structure for tiers 4 and 5 get really weird. Surely, there are some denormalizations that make things simpler, but as any denormalization, it limits further development.

While there is still a lot of room for improvement on Tier 2, if you are considering moving to Tier 3+, you are hereby warned: **Everybody falls the first time!**
