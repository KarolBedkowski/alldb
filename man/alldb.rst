==========
 alldb
==========

-----------------------------------
AllDB
-----------------------------------

:Author: Karol Będkowski
:Date:   2010-03-20
:Copyright: Copyright(c) Karol Będkowski, 2009-2010
:Version: 1.0
:Manual section: 1
:Manual group: AllDB Manual Pages


SYNOPSIS
========

alldb

DESCRIPTION
===========

AllDB is a very simple application for storing various information organised in 
some categories. Each category has own set of fields.

Main features:

* small, fast
* store all information in one, sqlite database
* import and export to the CSV files
* quick search by filter items list
* tagging item

This application is similar to the StuffKeeper (http://www.stuffkeeper.org/), but simpler and
portable (writen in Python and wxWidgets).


OPTIONS
=======

-d, --debug  Enable debug messages
-h, --help   Show help message and exit
--version    Show information about application version

FILES
=======

~/.local/share/alldb/alldb.db
    Application database, contain all stored information.

~/.config/alldb/alldb.cfg
    Application configuration file.
