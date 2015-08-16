#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Parse org-mode agendas, task lists, etc. and return simple reminders
to be included in environment status bar or shell.
"""

import re
import datetime as dt
import os
import orgnode
import itertools
from collections import defaultdict

from config import *


def load_data():
    "Load data from all agendas using orgnode"
    db = []
    for agenda in agenda_files:
        path = os.path.join(base, agenda)

        # Parse file tags
        file_projects = []
        with open(path, 'r') as f:
            for line in f:
                line = line.decode('utf-8')
                match = re.match('^#\+FILETAGS: (.*)$', line, flags=re.UNICODE)
                if match:
                    match = match.groups()[0].split(' ')
                    file_projects = [project.strip() for project in match]

        headlines = orgnode.makelist(path, todo_default=todos)

        # Decorate headlines with file-global tags
        for headline in headlines:
            headline.filetags = file_projects

        # Gather all
        db += headlines
    return db

def until(date, relative):
    """
    Return time difference taking into account that date might not have a time given.
    If so - assume end of day. `relative' always has a time.
    """

    # Decorate with time
    if type(date) == dt.date:
        date = dt.datetime(date.year, date.month, date.day, 23, 59, 59)

    delta = (date - relative).total_seconds()
    # If negative - then a past event.
    return date, delta / 60.0 / 60.0 / 24.0


def closest(date_list, relative):
    """
    Find closest future event relative to a given date.

    If event has 10 dates (recurring but irregularly) we are interested in the
    first incoming date. But it's used also for parsing single dates.
    """
    # Closest date - original
    closest_date = None

    # Closest date converted to datetime
    closest_converted_date = None

    # Time delta for closest date
    closest_delta = None

    for date in sorted(date_list):
        converted_date, days = until(date, relative)

        closest_date = date
        closest_converted_date = converted_date
        closest_delta = days

        if closest_delta < 0:
            # Past event, iterate more
            continue

        # This is a first future event, do not check more.
        break

    return {
        'converted_date': closest_converted_date,
        'date': closest_date,
        'delta': closest_delta
    }


def get_tasks(db):
    """
    Parse all events and gather unfinished tasks.
    """
    today = dt.datetime.today()

    tasks = []

    for entry in db:
        ##
        # Iterate over all entries
        # Start with filtering

        if not entry.todo:
            continue

        # Now, ignore ones marked as "done/finished/closed"
        if entry.todo in todos_done:
            continue

        # Ignore projects
        if entry.todo == project_todo:
            continue

        ##
        # Basic
        task = {
            'headline': entry.headline,
            'todo': entry.todo,
            'dates': [],
            'tags': entry.tags,
            'priority': entry.Priority() or None,
            'due': None,
            'projects': [],
        }

        if use_filetags_as_projects:
            task['projects'] = list(entry.filetags)

        ##
        # Scan parents for projects
        current = entry.parent
        while current:
            if current.todo == project_todo:
                if (use_short_headlines_as_projects and
                    current.headline.find(' ') == -1):
                    # Single word headline
                    task['projects'].append(current.headline)
                if use_tags_as_projects:
                    task['projects'] += list(current.tags)
            current = current.parent


        ##
        # Parse dates
        # Sorted from least `due-like' to most due-like
        types = [
            ('TIMESTAMP', entry.datelist),
            ('RANGE', [dr[0] for dr in entry.rangelist]),
            ('SCHEDULED', [entry.Scheduled()] if entry.Scheduled() else []),
            ('DEADLINE', [entry.Deadline()] if entry.Deadline() else []),
        ]

        for datetype, dates in types:
            if not dates:
                continue

            date = closest(dates, relative=today)

            date.update({
                'eventtype': datetype,
                'entry': entry,
            })

            if date:
                task['due'] = date

            task['dates'].append(date)

        tasks.append(task)


    return tasks


def export_todotxt(tasks):

    # Sort
    def key(t):
        return (t['priority'] or default_priority,
                t['due']['converted_date'] if t['due'] else dt.datetime(9999, 12, 31),
                todos.index(t['todo']))

    tasks.sort(key=key)

    # Export
    for task in tasks:
        s = []
        if task['priority']:
            s.append('(%s)' % task['priority'])
        s.append(task['headline'])

        if task['due']:
            d = task['due']['converted_date'].strftime('%Y-%m-%d')
            s.append('due:%s' % d)

        for tag in task['tags']:
            s.append('@' + tag)

        for project in task['projects']:
            s.append('+' + project)

        s = " ".join(s)
        print s.encode('utf-8')

def main():
    u"Convert org entries into todo2txt file"
    db = load_data()
    tasks = get_tasks(db)
    export_todotxt(tasks)


if __name__ == "__main__":
    main()
