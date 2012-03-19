#!/usr/bin/env python

# update.py

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
import tarfile
import sqlite3
import datetime
import re
import glob

from collections import defaultdict

from config import *

def merge_or_move_file(path,file_name):
	distr_file_path = C_distribute_dir+file_name
	tmp_file_path = path+file_name
	
	if not os.path.exists(tmp_file_path):
		txt = 'Error: '+file_name+' could not be found at path: '+tmp_file_path
        	print txt
        	write_logfile(txt)

	else: 
		tmp_FILE = open(tmp_file_path, "r")

		if not (os.path.exists(distr_file_path)):
			distr_FILE = open(distr_file_path, "w") 
        		for line in tmp_FILE:
        			if line.strip():
                			if not line.startswith('#'):
						distr_FILE.write(line)
	
                	tmp_FILE.close()
                	distr_FILE.close()

		else:
			distr_FILE = open(distr_file_path, "r")
			tmp = distr_FILE.readlines()
			distr_FILE.close()
                	distr_FILE = open(distr_file_path, "a")
			for line in tmp_FILE:
				if line.strip():
                                	if not line.startswith('#'):
						if line not in tmp:
							distr_FILE.write(line)
		
			tmp_FILE.close()
                	distr_FILE.close()
 
def write_logfile(txt):
	FILE = open(C_updatelog,'a')
        FILE.write(str(txt)+'\n')
        FILE.close()

def check_md5(md5,file_name):
	if os.path.exists(file_name):
		txt = "Comparing md5 checksums..."
		print txt
		write_logfile(txt)
		FILE = open(file_name,"r")
		if not (cmp(FILE.readline(),md5) == 0):
			FILE.close()
			FILE = open(file_name,"w")
                	FILE.write(md5)
                	FILE.close()
			return True
		else:
			FILE.close()
			return False
	else:	
        	FILE = open(file_name,"w")
        	FILE.write(md5)
        	FILE.close()
		return True

def download_md5(url):
	try:
		txt = "Dowloading md5: "+url
                print txt
                write_logfile(txt)
        	md5 = urllib2.urlopen(url).read().replace('"','')
		return md5 
	except urllib2.HTTPError, e:
		txt = 'HTTP Error: '+str(e)
        	print txt
		write_logfile(txt)
	except urllib2.URLError, e:
        	txt = 'URL Error: '+str(e)
		print txt
                write_logfile(txt)

def download_rules(url,filename):
	try:
		txt = "Downloading rules: "+url
		print txt
                write_logfile(txt)
		tmp = urllib2.urlopen(url)
		FILE = open((C_tmp_dir+filename),"w")
		FILE.write(tmp.read())
		FILE.close()
		return True
	except urllib2.HTTPError, e:
        	txt = 'HTTP Error: '+str(e)
		print txt
                write_logfile(txt)
		return False
	except urllib2.URLError, e:
        	txt = 'URL Error: '+str(e)
		print txt
                write_logfile(txt)
		return False

def extract_file(filename,name):
	try:
		txt = 'Extracting files...'
		print txt
                write_logfile(txt)
		FILE = tarfile.open((C_tmp_dir+filename),'r:gz')
		FILE.extractall(C_tmp_dir+name)
		FILE.close()
		return True
	except StandardError, e:
		txt = "TAR Error:",e
		print txt
                write_logfile(txt)
		return False
 
def find(regex, string):
	res = re.search(regex, string)
        if not (res is None):
                res = ((res.group()).strip())
        else:
                res = 'none'
        return  res

def find_ref(string):
	ref_tmp = re.findall(r'(?<=reference:)(.*?)(?=;)', string)
        ref = ''

	if not os.path.exists(C_distribute_dir+'reference.config'):
		for hit in ref_tmp:
			ref = ref+'  '
	
	else:
		for hit in ref_tmp:
			FILE = open((C_distribute_dir+'reference.config'), 'r')
			hit = hit.strip('http')
			hit = hit.strip('https')
			key = re.match(r'(.*?)(?=,)',hit).group()
			url_lastpart = re.search(r'(?<=\,).*',hit).group()
			url_firstpart = ''
			regex = r'(?<=%s).*' % key
			for line in FILE:
				tmp = re.search(regex,line,re.IGNORECASE)
				if tmp is not None:
					url_firstpart = tmp.group()
			
			ref = ref+('<a rel="nofollow" target="_blank" href="'+url_firstpart.strip()+url_lastpart.strip()+'" target="_blank">'+key.upper()+'</a>, ')
			FILE.close()
        return ref

def read_rule_files(path,source):
	txt = "Reading in rules..."
	print txt
        write_logfile(txt)
	rules = []
	filepaths = glob.glob(path+'*.rules')
 	for filepath in filepaths:
		ruleset = os.path.basename(filepath).replace('.rules', '').replace('emerging-', '')
		FILE = open(filepath,"r")
		for line in FILE:
			if line.strip():
				if not line.startswith('#'):
                        		sid = find(r'(?<=[^l]sid:)(.*?)(?=;)',line)
                        		rev = find(r'(?<=rev:)(.*?)(?=;)',line)
                                	name = find(r'(?<=msg:")(.*?)(?=";)',line)
					ref = find_ref(line.lower())
					rules.append([sid,rev,source,ruleset,name,ref,date,line])
		FILE.close()
	return rules

def insert_into_db(rules):
        txt = "Inserting rules into db..."
	print txt
        write_logfile(txt)

	db = sqlite3.connect(C_db_path)
        cursor = db.cursor()
	
	for line in rules:
		sid,rev,source,ruleset,name,ref,date,rule = line
		
		try:
			cursor.execute("SELECT sidnr, revnr FROM rules WHERE sidnr = (?) ", [sid])
			res = cursor.fetchone()
		except StandardError, e:
                	txt = "Exiting with error: "+str(e)
			print txt
        		write_logfile(txt)
                	sys.exit()

		if res is None:  #if true = new sid
                      	try:
				cursor.execute('''INSERT INTO rules (sidnr,revnr,source_name,ruleset_name,rule_name,ref,date,rule_syntax) 
				VALUES(?,?,?,?,?,?,?,?)''',[sid,rev,source,ruleset,name,ref,rule_date,rule])
			except StandardError, e:
                        	txt = "Exiting with error: "+str(e)
				print txt
        			write_logfile(txt)
                        	sys.exit()

                elif (res[1] is not None):
			if not res[1] < rev:  #if true = old sid, but new/higher rev
				try:
					cursor.execute('''UPDATE rules SET revnr = (?), source_name = (?), ruleset_name = (?), 
					rule_name = (?),  ref = (?), date = (?), rule_syntax =(?) WHERE sidnr = (?)''',
					[rev,source,ruleset,name,ref,rule_date,rule,sid])
				except StandardError, e:
                                	txt = "Exiting with error: "+str(e)
					print txt
        				write_logfile(txt)
                                	sys.exit()

	db.commit()
	cursor.close()
	db.close()
	txt = 'Finished. success!'
	print txt
        write_logfile(txt)

	
#### FUNCTIONS END ####


#### GLOBAL VARIABLES START ####
now = datetime.datetime.now()
date = '%d:%d %d/%d/%d' % (now.hour,now.minute,now.day,now.month,now.year)
rule_date = now.strftime("%Y-%m-%d")

#### GLOBAL VARIABLES END ####


#### MAIN START ####
txt = "Rule update started: "+date
print txt
write_logfile(txt)

#operations on local rule source
if not (C_locale_rule_path == ''):
	txt = 'Updating rules for source: local'
        print txt
        write_logfile(txt)
	insert_into_db(read_rule_files(C_locale_rule_path,'local'))

#operations on external rule sources
for source in C_rule_sources:
	source_name, md5_url, rule_url, rules_path, files_path = source
	source_name = source_name.lower().replace(' ', '')
	txt = 'Updating rules for source: '+source_name
	print txt
	write_logfile(txt)

	if not (md5_url == ''):
		if check_md5((download_md5(md5_url)),(C_tmp_dir+source_name+'.md5')):
			if not (download_rules(rule_url,(source_name+'.tar.gz')) is False):
				if not (extract_file((source_name+'.tar.gz'),source_name) is False):
					if not (files_path == 'none'):
						txt = 'Starting operations on .conf and .map files...'
						print txt
                				write_logfile(txt)
						for f in C_files:
							merge_or_move_file((C_tmp_dir+source_name+'/'+files_path),f[0])
						txt = 'Done. Files have been moved or merged'
                                        	print txt
                                        	write_logfile(txt)

					insert_into_db(read_rule_files((C_tmp_dir+source_name+'/'+rules_path),source_name))
		else:
			txt = "No new rules to download"
			print txt
			write_logfile(txt)
	else:
		txt = 'Skipping md5 check'
		print txt
		write_logfile(txt)

		if not download_rules(rule_url,(source_name+'.tar.gz')) is False:
			if not (extract_file((source_name+'.tar.gz'),source_name) is False):
                           	if not (files_path == 'none'):
                                   	txt = 'Starting operations on .conf and .map files...'
                                       	print txt
                                       	write_logfile(txt)
                                      	for f in C_files:
                                              	merge_or_move_file((C_tmp_dir+source_name+'/'+files_path),f[0])
					txt = 'Done. Files have been moved or merged'
                                     	print txt
                                      	write_logfile(txt)

				insert_into_db(read_rule_files((C_tmp_dir+source_name+'/'+rules_path),source_name))
		else:
			txt = "No new rules to download"
			print txt
			write_logfile(txt)
	
#### MAIN END ####
