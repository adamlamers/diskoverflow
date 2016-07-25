#Disk Overflow

This is an offline viewer for StackOverflow data dumps. It utilizes sqlite3's FTS4 functionality as
the backend for searching questions.

There are 3 components:
* stackexchange_to_sqlite3_iterparse.py
    * This file will take the [StackOverflow data dump from
      archive.org](https://archive.org/details/stackexchange) and add it to a SQLite 3 database with
      full-text search indexes.
* app.py
    * This is the Flask backend that handles running queries on the data.
* templates/index.html
    * The actual application. The goal is to be one-page, with fast real-time filtering as you type,
      or at least as close to that as possible.


TODO:
    * Optimize queries for speed on initial keyword searches
    * Find the best way to real-time filter queries, when the best threshold to begin searching is
    * Automatically fuzzy search words so things like sqlite also search sqlite3 and so on
    * Discard questions with no answers to help decrease the database size. Current imported size as
      of July 2016 is ~85GB with all questions/answers from stackoverflow.
