#!/usr/bin/env python

# distribute.py

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

import os
import sys
import urllib2
import sqlite3
import datetime
import subprocess

from config import *

#### FUNCTIONS START ####
def write_logfile(txt):
        FILE = open(C_distrblog,'a')
        FILE.write(str(txt)+'\n')
        FILE.close()

def get_sensors():
        db = sqlite3.connect(C_db_path)
        cursor = db.cursor()

	try:
		txt = "Collecting sensor information..."
                print txt
                write_logfile(txt)
        	cursor.execute('SELECT * FROM sensors')
                all_sensors = cursor.fetchall()
		return all_sensors

	except StandardError, e:
                txt = 'Exiting with error: '+str(e)
                print txt
                write_logfile(txt)
                sys.exit()

        cursor.close()
        db.close()

def get_rules(sname):
        db = sqlite3.connect(C_db_path)
        cursor = db.cursor()
        
	try:
		sql = 'SELECT sid FROM '+sname+'_disabled'
		cursor.execute(sql)
                tmp = cursor.fetchall()
                txt = 'Disabled rule count: '+str(len(tmp))
		print txt
                write_logfile(txt)
		disabled = ",".join(str(x[0]) for x in tmp)
		sql = 'SELECT rule_syntax FROM rules WHERE sidnr NOT IN ('+disabled+')'
		cursor.execute(sql)
		rules = cursor.fetchall()
		txt = 'Enabled rule count: '+str(len(rules))
                print txt
                write_logfile(txt)
		return rules

	except StandardError, e:
                txt = 'Exiting with error: '+str(e)
                print txt
                write_logfile(txt)
                sys.exit()
	
        cursor.close()
        db.close()

def create_dir(name):
	try:
                if not os.path.isdir(name):
			txt = 'Creating directory: '+name
                	print txt
                	write_logfile(txt)
			os.mkdir(name)
		
	except StandardError, e:
                txt = 'Exiting with error: '+str(e)
                print txt
                write_logfile(txt)
                sys.exit()

def write_rules(sname,rules):
	try:
		dir_name = C_distribute_dir+sname+'/'
		create_dir(dir_name)

		txt = 'Writing '+sname+'.rules...'
                print txt
                write_logfile(txt)
		
		FILE = open(dir_name+sname+'.rules', "w")

		for rule in rules:
			FILE.write(rule[0])
		
 		FILE.close()
			
	except StandardError, e:
                txt = 'Exiting with error: '+str(e)
                print txt
                write_logfile(txt)
                sys.exit()

def get_threshold(sname):
        db = sqlite3.connect(C_db_path)
        cursor = db.cursor()

        try:
		txt = 'Checking for threshold and suppress rules...'
                print txt
                write_logfile(txt)

                sql = 'SELECT syntax FROM '+sname+'_threshold'
                cursor.execute(sql)
                threshold = cursor.fetchall()

                txt = 'Threshold/suppress rule count: '+str(len(threshold))
                print txt
                write_logfile(txt)

		if not str(len(threshold)) == '0':
                	return threshold
		else:
			return False

        except StandardError, e:
                txt = 'Exiting with error: '+str(e)
                print txt
                write_logfile(txt)
                sys.exit()

        cursor.close()
        db.close()

def write_threshold(sname,threshold):
        try:
                dir_name = C_distribute_dir+sname+'/'

		if len(threshold) is not '0':
                	txt = 'Writing threshold.conf...'
                	print txt
                	write_logfile(txt)

                	FILE = open(dir_name+'threshold.conf', "w")

      			for rule in threshold:
                        	FILE.write(rule[0]+'\n')

                	FILE.close()

        except StandardError, e:
                txt = 'Exiting with error: '+str(e)
                print txt
                write_logfile(txt)
                sys.exit()

def transfer_files(dir_name,dest):
	try:
		for file in os.listdir(dir_name):
                        if '.' in file:
				txt = 'Syncing file: '+file
                                print txt
                              	write_logfile(txt)
                                
				tmp = dir_name+file
                                
				p = subprocess.Popen(["rsync","-auvz","-e","ssh",tmp,dest],stdout=subprocess.PIPE)
                                for line in p.stdout:
					if line.replace('\n','').strip():
                                        	txt = line
                                        	print txt
                                        	write_logfile(txt)
                                p.stdout.close()

	except StandardError, e:
                txt = 'Error: '+str(e)
                print txt
                write_logfile(txt)

def distribute(sname,ip,path,uname):
	try:	
		dest = uname+'@'+ip+':'+path

		txt = 'File transfer started...'
        	print txt
        	write_logfile(txt)

		transfer_files(C_distribute_dir,dest)
		transfer_files(C_distribute_dir+sname+'/',dest)

	except StandardError, e:
                txt = 'Error: '+str(e)
                print txt
                write_logfile(txt)

def reload_rules(ip,uname,cmd):
	try:
		txt = 'Reloading rules on sensor...'
                print txt
                write_logfile(txt)

		command = cmd+' && exit'

		p = subprocess.Popen(["ssh","-x","-l",uname,ip,command],stdout=subprocess.PIPE)
               	for line in p.stdout:
                  	txt = line+'\n'
                       	print txt
                      	write_logfile(txt)
              	p.stdout.close()

	except StandardError, e:
                txt = 'Error: '+str(e)
                print txt
                write_logfile(txt)

#### FUNCTIONS END ####


#### GLOBAL VARIABLES START ####
now = datetime.datetime.now()
date = '%d:%d %d/%d/%d' % (now.hour,now.minute,now.day,now.month,now.year)

#### GLOBAL VARIABLES END ####


#### MAIN START ####
txt = "Rule distribution started: "+date
print txt
write_logfile(txt)

all_sensors = get_sensors()
for sensor in all_sensors:
	sname,ip,path,uname,cmd = sensor
	txt = 'Gathering rules for sensor: '+sname
        print txt
        write_logfile(txt)
	write_rules(sname,get_rules(sname))
	threshold = get_threshold(sname)
	if threshold is not False:
		write_threshold(sname,threshold)
	distribute(sname,ip,path,uname)
	reload_rules(ip,uname,cmd)
	txt = 'Done.'
        print txt
        write_logfile(txt)

	
#### MAIN END ####
