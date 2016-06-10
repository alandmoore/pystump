=========
 PyStump
=========

------------------------------
Simple web-based announcements
------------------------------


What is it?
===========

PyStump is a web service for displaying announcement slides, such as for a digital signage kiosk.  PyStump is designed to be updated and edited all in a browser.

Some interesting features include:

- LDAP (Active Directory, eDirectory) or SQLite logins
- Text auto-sizes to fit any screen size
- Background can be an image or solid color
- Animated transitions
- Slides can be activated and expired automatically by date/time

PyStump is built on Flask, Python, and SQLite.

Much of PyStump's codebase was originally borrowed from another project, `OmegaHymnal <http://www.alandmoore.com/omegahymnal/omegahymnal.html>`_.


Who would use this?
===================

Any organization -- workplaces, schools, stores, restaurants, churches, libraries, government buildings, etc --  that has information to communicate to a large group of people can make use of PyStump.  Display announcements and upcoming events, highlight specials or sales, give encouraging words or instructions -- say what you want to say.

Any number of simple kiosks (computers running a full-screen web browser) can be pointed to a single web server running PyStump, where authorized users can update the announcements using a web browser.

Users can be authenticated using Microsoft Active Directory, Novell eDirectory, or users/passwords stored in SQLite, so it can be flexible to a wide variety of organizations.



Installation
============

See the included INSTALL.rst file.


License
=======

PyStump is released under the GNU GPL v3.  Please see the attached COPYING document for details.


Authors
=======

PyStump is primarily the work of `Alan D Moore <http://www.alandmoore.com>`_.


Included in the source tree are some javascript/css libraries by third parties:

- `jQuery <http://jquery.com>`_
- `jQuery-ui <http://jqueryui.com>`_
- `jQuery Timepicker Addon <http://trentrichardson.com/examples/timepicker/>`_ by Trent Richardson
- `CKEditor <http://ckeditor.com>`_


Bugs, Features, Contributions
=============================


Bugs should be reported as issues to the GitHub repository.

If you would like to see a new feature added to PyStump, you have three options:

- Fork the project, code the feature, and make a pull request.
- Arrange for a talented python coder to do the above, making sure to compensate the individual for his/her time.
- Hope and pray that someone else needs your feature and does one of the above.

All code contributions are appreciated.  If you contribute a patch, please make sure to add your name to the Authors section.
