Quality Assurance
#####################

This project is now close to five years old and, as any continuously
developed project, has legacy issues. If anyone tells you that their
project has no legacy issues, they are either ignorant or lying. 
Probably both.

Here is how issues are reduced, caught and fixed in this project.

Test coverage, Continuous Integration, Continuous Deployment
=================================================================

Test Coverage
++++++++++++++++++++++

For years, test coverage was around 99% (mostly functional tests), and 
the goal is to keep it over 99.5% (rounded to 100%) for major releases.

Continuous Integration
++++++++++++++++++++++++++++++

These tests are run on every push to the code repository, 
(together with code style validation).

Manual Testing
++++++++++++++++++++++++++++++++

Before each major release, all functionality is manually tested.

Of course, there is a small chance that some edge case is not covered,
and that someone will hit a bug in production, but it is reduced to the
minimum.

Code Style, Complexity and Maintainability
========================================================

Some of these issues can be detected and/or measured, sometimes even 
fixed, with standard tools. Code style, complexity and maintainability 
are good examples.

Code Style
+++++++++++++++++
Code style in this project is current Black, with line length of 79 
characters. This is validated on every push.

Code Complexity
++++++++++++++++++

Recently, code complexity has been improved. No code block has nor should 
have complexity over ``C (20)``. Average should remain around ``A (3.0)``.

Code Maintainability
+++++++++++++++++++++++++

Code maintainability is to be improved, currently 2 files have dead low 
index, due to their size. The goal is to have ``A`` across all files for 
the next major release (in 2024).
