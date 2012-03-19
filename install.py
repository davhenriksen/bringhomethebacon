#!/usr/bin/env python

# install.py

#    bring home the bacon Copyright (C) 2012 David Ormbakken Henriksen (davidohenriksen@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import sqlite3
import sys

from config import *

def create_db():
        try:
                print "Creating database with tables..."
                con = sqlite3.connect(C_db_path)
                cursor = con.cursor()
                cursor.execute("""CREATE TABLE rules(
                        sidnr INTEGER,
                        revnr INTEGER,
                        source_name TEXT,
                        ruleset_name TEXT,
                        rule_name TEXT,
                        ref TEXT,
                        date TEXT,
                        rule_syntax TEXT,
                        PRIMARY KEY (sidnr))""")
                cursor.execute("""CREATE TABLE sensors(
                        sname TEXT,
                        ip TEXT,
                        path TEXT,
                        uname TEXT,
                        cmd TEXT,
                        PRIMARY KEY (sname))""")
        except StandardError, e:
                print "Exiting with error: ", e
                sys.exit()

	con.commit()
        cursor.close()
        con.close()
	print "Successfully created sms.db"


# MAIN
print "Installing..."
create_db()
print "Install finished"
