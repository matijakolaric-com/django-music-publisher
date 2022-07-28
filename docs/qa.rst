Quality Assurance
#####################

This project is now over four years old and, as any continuously
developed project, has legacy issues. If anyone tells you that their
project has no legacy issues, they are either ignorant or lying. 
Probably both.

Here is how they are reduced, caught and fixed in this project.

Test coverage, Continuous Integration, Continuous Deployment
=================================================================

For years, test coverage was around 99% (mostly functional tests), and 
the goal is to keep it over 99.5% (rounded to 100%) for major releases.

These tests are run on every push to the code repository, 
(together with code style validation). If tests pass, the code
is automatically deployed. 

This instance is used for creating screenshots for documentation 
and videos, and before each major release, all functionality is
manually tested.

Of course, there is a small chance that some edge case is not covered,
and that someone will hit a bug in production, but it is reduced to the
minimum.

Code Style, Complexity and Maintainability
========================================================

Some of these issues can be detected and/or measured, sometimes even 
fixed, with standard tools. Code style, complexity and maintainability 
are good examples.

Code style in this project is current Black, with line length of 79 
characters. This is validated on every push.

Recently, code complexity has been improved. No code block has nor should 
have complexity over ``C (20)``. Average should remain around ``A (3.0)``.

Code maintainability is to be improved, currently 2 files have dead low 
index, due to their size. The goal is to have ``A`` across all files by
the 23.4 release.

Creativity of the one obvious way to do it
=====================================================================

All of these measures are about reducing the possibility of an issue
arising, catching it when it does, and fixing it quickly without
breaking something else. But, it has nothing to do with actual 
development of new features. 

Breaking the presumptions
++++++++++++++++++++++++++++++++++++++++++++++++

Until 2018, CWR was seen as something that only large
publishers can use, due to it's complexity and expensive tools.
Then DMP came out and shattered this, making CWR free and available
to small publishers. In 2022, the mainstream belief in music
publishing is that CWR is for everyone.

Until 2020, most of the industry has believed that royalty management
for music publishers is ... well, you know, only available to large 
publishers, due to complexity and price.

Until 2022 ... data exchange between publishers and labels ... 
complex and expensive.

QA without rules
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The question is how to assure quality if there are no standards and no 
expectations that actually apply to your project? 
(Except that it is impossible. Again.)

Well, DMP fulfills all those that do apply (like CWR or DDEX EBR specs),
validate everything can be validated (IPI, ISWC, DPID), except when
breaking the rules is advantageous. (There is a reason why nearly everyone 
believed something was impossible, until someone broke some rule.) 

But, most of the rules are great, choosing which ones to break
is a long process, in the three examples above, this choice took 
many years.

And, if you break a rule, you must make a new one and document it really
well.






