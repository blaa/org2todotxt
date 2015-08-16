
org-mode to ToDoTXT converter
=============================

This program:
*  Converts org-mode headlines to todotxt "tasks".
*  Sets due:... dates using DEADLINES, SCHEDULED or generic timestamps
*  Sets @tags using entries tags
*  Sets +project tags using file-wide FILETAGS or dedicated "headline type" (todo=PROJECT)
*  Decorates tasks with A,B,C priorities
*  Sorts tasks by priority, due date and todo-type.

Can be probably used for:
*  One-way synchronising your desktop org-mode data with mobile devices which increasingly
support todo2txt.
*  Support synchronisation back using some shared folder and for example orgzly.
*  I use it because I sincerely HATE having UUID on each org-mode entry which is required for caldav-sync.

Org-mode has multiple ways of storing the same information as todotxt
and many information are lost in the progress. You'll probably be
using org-mode differerently than I do so please copy
config.py_template to config.py and adjust accordingly and don't
hesitate to alter the program itself - it's simple.

Set it to run from CRON or from some inotify event.

Parsing is based on orgnode by Charles Cave, Takafumi Arakaki, Albin Stjerna

Have fun.


