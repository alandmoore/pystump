=========
 PyStump
=========

------------------------------
Simple web-based announcements
------------------------------


What is it?
===========

PyStump is a web service for displaying announcement slides, such as for a digital signage kiosk.  PyStump is designed to be updated and edited all in a browser.

PyStump is built on Flask, Python, and SQLite.

Much of PyStump's codebase was originally borrowed from another project, `OmegaHymnal <http://www.alandmoore.com/omegahymnal/omegahymnal.html>`.


Who would use this?
===================

An example might be an organization that wants to display announcements on digital signage.  Kiosks could be pointed to a web server running PyStump, and authorized users could update the announcements using their web browser.

The authorization backends supported at this point include Active Directory and eDirectory.  Other authorization backends may be added at some point.


Installation
============

See the included INSTALL.rst file.


License
=======

PyStump is released under the GNU GPL v3.  Please see the attached COPYING document for details.


Authors
=======

PyStump is primarily the work of `Alan D Moore <http://www.alandmoore.com>`.


Included in the source tree are some javascript/css libraries by third parties:

- `jQuery <http://jquery.com>`
- `jQuery-ui <http://jqueryui.com>`
- `jQuery Timepicker Addon <http://trentrichardson.com/examples/timepicker/>` by Trent Richardson



Bugs, Features, Contributions
=============================


Bugs should be reported as issues to the GitHub repository.

If you would like to see a new feature added to PyStump, you have three options:

- Fork the project, code the feature, and make a pull request.
- Arrange for a talented python coder to do the above, making sure to compensate the individual for his/her time.
- Hope and pray that someone else needs your feature and does one of the above.

All code contributions are appreciated.  If you contribute a patch, please make sure to add your name to the Authors section.
