#!/usr/bin/env python

# web.py

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
import sqlite3
import re
import sys
import subprocess

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.autoreload

import simplejson as json
from tornado.options import define, options


define("port", default=8080, help="run on the given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
		(r"/", MainHandler),
		(r"/rulesets", RulesetsHandler),
		(r"/rules", RulesHandler),
		(r"/sensors", SensorsHandler),
		(r"/get_rulesets", GetRulesetsHandler),
		(r"/get_rules", GetRulesHandler),
		(r"/get_sensors", GetSensorsHandler),
		(r"/add_sensor", AddSensorHandler),
		(r"/remove_sensor", RemoveSensorHandler),
		(r"/open_rule", OpenRuleHandler),
		(r"/getsensorname", GetSensorNameHandler),
		(r"/tuning_rules", TuningRulesHandler),
		(r"/tuning_rulesets", TuningRulesetsHandler),
		(r"/update_sensor", UpdateSensorHandler),
		(r"/update", UpdateHandler),
		(r"/atuninghelp", ATuningHelpHandler),
		(r"/suppress", SuppressHandler),
		(r"/threshold", ThresholdHandler),
		(r"/atuning", ATuningHandler),
		(r"/get_atuning", GetATuningHandler),
		(r"/remove_atuning", RemoveATuningHandler),
		(r"/distribute", DistributeHandler),
		]
        	settings = dict(
            	#login_url="/auth/login",
            	template_path=os.path.join(os.path.dirname(__file__), "templates"),
            	static_path=os.path.join(os.path.dirname(__file__), "static"),
	    	autoescape=None)
        	tornado.web.Application.__init__(self, handlers, **settings)

class RemoveATuningHandler(tornado.web.RequestHandler):
        def post(self):
                syntax = self.request.arguments.get("atuningid")

                db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

                try:
			cursor.execute('SELECT sname FROM sensors')
                        all_sensors = cursor.fetchall()
                        for hit in all_sensors:
                                table = hit[0]+'_threshold'
				sql = 'DELETE FROM %s WHERE syntax="%s"' % (table,syntax[0])
				cursor.execute(sql)

                        db.commit()

                except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('RemoveATuningHandler ERROR: '+str(e)+'\n')
                        FILE.close()

                cursor.close()
                db.close()

class GetATuningHandler(tornado.web.RequestHandler):
        def get(self):
                db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

                atuning = []

                try:
			cursor.execute('SELECT sname FROM sensors')
                        all_sensors = cursor.fetchall()
                        for hit in all_sensors:
                        	table = hit[0]+'_threshold'
				sql = 'SELECT * FROM '+table
                        	cursor.execute(sql)
                        	for row in cursor:
                                	idnr,sid,typ,syntax,comment,sensor = row
                                	check = "<center><input type='checkbox' name='atuningid' value='%s'></center>" % (syntax)
                                	tmp = (check,sid,typ,syntax,comment,sensor)
					if tmp not in atuning:
                                		atuning.append(tmp)

                except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('GetATuningHandler ERROR: '+str(e)+'\n')
                        FILE.close()

                cursor.close()
                db.close()
                self.write(json.dumps({"aaData":atuning},sort_keys=True,indent=4))

class ThresholdHandler(tornado.web.RequestHandler):
        def post(self):
                db = sqlite3.connect('../DB.db')
                cursor = db.cursor()	
		
                if 'sigid' not in self.request.arguments:
                        self.write('Input missing. Try again.')
		
		elif 'count' not in self.request.arguments:
                        self.write('Input missing. Try again.')
		
		elif 'sec' not in self.request.arguments:
                        self.write('Input missing. Try again.')
		
		else:
			genid = self.request.arguments.get("genid")
                        sigid = self.request.arguments.get("sigid")
                        typ = self.request.arguments.get("type")
                        track = self.request.arguments.get("track")
                        count = self.request.arguments.get("count")
                        sec = self.request.arguments.get("sec")
                        sensor = self.request.arguments.get("select")
			comment = ''

			if 'comment' in self.request.arguments:
				tmp = self.request.arguments.get("comment")
				comment = tmp[0]

                        syntax = 'event_filter gen_id '+genid[0]+',sig_id '+sigid[0]+',type '+typ[0]+',track '+track[0]+',count '+count[0]+',seconds '+sec[0]

			try:
				def insert_t(table,x):
                  			sql = 'INSERT OR IGNORE INTO '+table+' (id,sid,type,syntax,comment,sensor) VALUES (null,'+sigid[0]+',"threshold","'+syntax+'","'+comment+'","'+x+'")'
					cursor.execute(sql)
				
				if not (sensor[0] == "all"):
                                	table = sensor[0]+'_threshold'
					insert_t(table,sensor[0])
				
				else:
					cursor.execute('SELECT sname FROM sensors')
                                	all_sensors = cursor.fetchall()
                                	for hit in all_sensors:
						table = hit[0]+'_threshold'
						insert_t(table,'ALL')

				db.commit()
				self.write('threshold rule for sid: '+sigid[0]+' has been added!')

			except StandardError,e:
                        	FILE = open('weberrorlog.txt','a')
                        	FILE.write('ThresholdHandler ERROR: '+str(e)+'\n')
                        	FILE.close()
				self.write(str(e))

		cursor.close()
                db.close()

class SuppressHandler(tornado.web.RequestHandler):
	def post(self):
		db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

                if 'sigid' not in self.request.arguments:
                        self.write('Input missing. Try again.')

		elif 'ip' not in self.request.arguments:
			self.write('Input missing. Try again.')

                else:
                        genid = self.request.arguments.get("genid")
                        sigid = self.request.arguments.get("sigid")
                        track = self.request.arguments.get("track")
                        ip = self.request.arguments.get("ip")
                        sensor = self.request.arguments.get("select")
                        comment = ''
			
			if 'comment' in self.request.arguments:
                                tmp = self.request.arguments.get("comment")
                                comment = tmp[0]

			syntax = 'suppress gen_id '+genid[0]+',sig_id '+sigid[0]+',track '+track[0]+',ip '+ip[0]

                        try:
                                def insert_t(table,x):
                                        sql = 'INSERT OR IGNORE INTO '+table+' (id,sid,type,syntax,comment,sensor) VALUES (NULL,'+sigid[0]+',"suppress","'+syntax+'","'+comment+'","'+x+'")'
                                        cursor.execute(sql)

                                if not (sensor[0] == "all"):
                                        table = sensor[0]+'_threshold'
                                        insert_t(table,sensor[0])

                                else:
                                        cursor.execute('SELECT sname FROM sensors')
                                        all_sensors = cursor.fetchall()
                                        for hit in all_sensors:
                                                table = hit[0]+'_threshold'
                                                insert_t(table,'ALL')

                                db.commit()
                                self.write('suppress rule for sid: '+sigid[0]+' has been added!')

                        except StandardError,e:
                                FILE = open('weberrorlog.txt','a')
                                FILE.write('ThresholdHandler ERROR: '+str(e)+'\n')
                                FILE.close()
                                self.write(str(e))

                cursor.close()
                db.close()

class DistributeHandler(tornado.web.RequestHandler):
        def get(self):
                self.write('''<html  xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Distribute report</title>
<link type="text/css" rel="stylesheet" href="../static/css/custom.css"/>
<link type="text/css" rel="stylesheet" href="../static/css/demo_page.css"/>
</head>
<body>
&nbsp<b>Distribute report</b></br>''')

                try:
                        p = subprocess.Popen(["python","../distribute.py"], stdout=subprocess.PIPE)
                        for line in iter(p.stdout.readline, ''):
                                self.write('&nbsp')
                                self.write(line)
                                self.write('</br>')
                        p.stdout.close()

                except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('DistributeHandler ERROR: '+str(e)+'\n')
                        FILE.close()

                self.write('''</body>
</html>''')

		
class UpdateHandler(tornado.web.RequestHandler):
        def get(self):
		self.write('''<html  xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Update report</title>
<link type="text/css" rel="stylesheet" href="../static/css/custom.css"/>
<link type="text/css" rel="stylesheet" href="../static/css/demo_page.css"/>
</head>
<body>
&nbsp<b>Update Report</b></br>''')
		
		try:
                	p = subprocess.Popen(["python","../update.py"], stdout=subprocess.PIPE)
                	for line in iter(p.stdout.readline, ''):
                        	self.write('&nbsp')
				self.write(line)
				self.write('</br>')
			p.stdout.close()

		except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('UpdateHandler ERROR: '+str(e)+'\n')
                        FILE.close()

		self.write('''</body>
</html>''')

class UpdateSensorHandler(tornado.web.RequestHandler):
        def post(self):
		db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

		sensor = self.request.arguments.get("select")
		
		try:
			if not (sensor[0] != 'all'):
				cursor.execute('SELECT sname FROM sensors')
                        	all_sensors = cursor.fetchall()

                	def update(f,v,s):
                        	sql = 'UPDATE sensors SET '+f+'="'+v+'" WHERE sname="'+s+'"'
				cursor.execute(sql)

			if "ip" in self.request.arguments:
				ip = self.request.arguments.get("ip")
				if not (sensor[0] == 'all'):
					update("ip",ip[0],sensor[0])
				else:
					for hit in all_sensors:
						update("ip",ip[0],hit[0])

			if "path" in self.request.arguments:
                                path = self.request.arguments.get("path")
                                if not (sensor[0] == 'all'):
                                        update("path",path[0],sensor[0])
                                else:
                                        for hit in all_sensors:
                                                update("path",path[0],hit[0])

                        if "uname" in self.request.arguments:
                                uname = self.request.arguments.get("uname")
                                if not (sensor[0] == 'all'):
                                        update("uname",uname[0],sensor[0])
                                else:
                                        for hit in all_sensors:
                                                update("uname",uname[0],hit[0])

                        if "cmd" in self.request.arguments:
                                pw = self.request.arguments.get("cmd")
                                if not (sensor[0] == 'all'):
                                        update("cmd",cmd[0],sensor[0])
                                else:
                                        for hit in all_sensors:
                                                update("cmd",cmd[0],hit[0])		

			db.commit()	
			self.write('Sensor updated! Refresh page to see changes.')
 
		except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('UpdateSensorHandler ERROR: '+str(e)+'\n')
                        FILE.close()
			self.write(str(e))

                cursor.close()
                db.close()

class TuningRulesetsHandler(tornado.web.RequestHandler):
        def post(self):
                source_ruleset = self.request.arguments.get("rulesetid")
                sensor = self.request.arguments.get("sensor")
                action = self.request.arguments.get("action")
	
              	db = sqlite3.connect('../DB.db')
             	cursor = db.cursor()

		sids = ''

		try:
			def disable_sid(table,sid):
                		value = sid.split(',')
                   		for entry in value:
                      			sql = 'INSERT OR IGNORE INTO '+table+' (sid) VALUES ('+entry+')'
                             		cursor.execute(sql)

            		def enable_sid(table,sid):
                		sql = 'DELETE FROM '+table+' WHERE sid IN ('+sid+')'
                      		cursor.execute(sql)
			
			length = len(source_ruleset)
			counter = 1
			for hit in source_ruleset:
				split = hit.split('.')
				sql = 'SELECT sidnr from rules WHERE source_name="'+split[0]+'" AND ruleset_name="'+split[1]+'"'
				cursor.execute(sql)
				tmp = cursor.fetchall()
				sids = sids+(",".join(str(x[0]) for x in tmp))
				if not (counter == length):
					sids = sids+","
				counter += 1

                	if not (sensor[0] == 'all'):
                        	table = sensor[0]+'_disabled'
				if not (action[0] == "enable"): 
                        		disable_sid(table,sids)
				else:
					enable_sid(table,sids)
                	
			else:
				cursor.execute('SELECT sname FROM sensors')
                        	all_sensors = cursor.fetchall()
				for hit in all_sensors:
					table = hit[0]+'_disabled'
					if not (action[0] == "enable"):
                                		disable_sid(table,sids)
                        		else:
                                		enable_sid(table,sids)

			db.commit()
                
		except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('TuningRulesetsHandler ERROR: '+str(e)+'\n')
                        FILE.close()

		cursor.close()
                db.close()

class TuningRulesHandler(tornado.web.RequestHandler):
	def post(self):
		sids = self.request.arguments.get('sidnr')
                sensor = self.request.arguments.get('sensor')
                action = self.request.arguments.get('action')

		db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

		def disable_sid(table,sid):
			sql = 'INSERT OR IGNORE INTO '+table+' (sid) VALUES ('+sid+')'
			cursor.execute(sql)
			
		def enable_sid(table,sid):
			sql = 'DELETE FROM '+table+' WHERE sid='+sid
			cursor.execute(sql)
		
		try:
			if not (sensor[0] == "all"):
				table = sensor[0]+'_disabled'
				for sid in sids:
                        		if not (action[0] == "enable"):
                               			disable_sid(table,sid)
                                	else:
                               			enable_sid(table,sid)				
			else:
				cursor.execute('SELECT sname FROM sensors')
				all_sensors = cursor.fetchall()
				for hit in all_sensors:
					table = hit[0]+'_disabled'
					for sid in sids:
						if not (action[0] == "enable"):
							disable_sid(table,sid)					
						else:
							enable_sid(table,sid)

			db.commit()
                
		except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('TuningRulesHandler ERROR: '+str(e)+'\n')
                        FILE.close()
		
                cursor.close()
                db.close()

class GetSensorNameHandler(tornado.web.RequestHandler):
	def get(self):
            	db = sqlite3.connect('../DB.db')
             	cursor = db.cursor()

               	try:
                	cursor.execute('SELECT sname FROM sensors')
			selectbox = '<select name="select" id="select"><option value="all">all sensors</option>'
			for sensor in cursor:
				selectbox = selectbox+'<option value="'+sensor[0]+'">'+sensor[0]+'</option>'
			
			selectbox = selectbox+'</select>'
			self.write(selectbox)
                except StandardError,e:
                        FILE = open("weberrorlog.txt","a")
                        FILE.write("GetSensorNameHandler ERROR: "+str(e)+"\n")
                        FILE.close()
			self.write('<select><option>ERROR</option></select>')

		cursor.close()
                db.close()
		
class OpenRuleHandler(tornado.web.RequestHandler):
	def get(self):
		sid = self.get_argument("sid")
                db = sqlite3.connect('../DB.db')
                cursor = db.cursor()
                
		try:
                	cursor.execute('SELECT rule_syntax FROM rules WHERE sidnr = (?)', [sid])
                        rulesyntax = cursor.fetchone()
			self.render("open_rules.html",rulesyntax=rulesyntax[0])
                
		except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('OpenRuleHandler ERROR: '+str(e)+'\n')
                        FILE.close()
		
		cursor.close()
                db.close()

class RemoveSensorHandler(tornado.web.RequestHandler):
        def post(self):
		snames = self.request.arguments.get("sensorid")
		
		db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

		try:
			for sensor in snames:
				sql = 'DELETE  FROM sensors WHERE sname="%s"' % (sensor)
				cursor.execute(sql)
				sql = 'DROP TABLE %s_disabled' % (sensor)
                        	cursor.execute(sql)
                        	sql = 'DROP TABLE %s_threshold' % (sensor)
				cursor.execute(sql)
			
			db.commit()

		except StandardError,e:
               		FILE = open('weberrorlog.txt','a')
                      	FILE.write('RemoveSensorHandler ERROR: '+str(e)+'\n')
                       	FILE.close()

                cursor.close()
                db.close()

class AddSensorHandler(tornado.web.RequestHandler):
	def post(self):
		db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

		if 'sname' not in self.request.arguments:
			self.write('Sensor NOT added. Input missing. Try again.')

		elif 'ip' not in self.request.arguments:
                        self.write('Sensor NOT added. Input missing. Try again.')

		elif 'path' not in self.request.arguments:
                        self.write('Sensor NOT added. Input missing. Try again.')

		elif 'uname' not in self.request.arguments:
                        self.write('Sensor NOT added. Input missing. Try again.')

		elif 'cmd' not in self.request.arguments:
			self.write('Sensor NOT added. Input missing. Try again.')
			
		else:
			sname = self.request.arguments.get("sname")
			sname = sname[0]
			ip = self.request.arguments.get("ip")
			ip = ip[0]
			path = self.request.arguments.get("path")
			path = path[0]
			uname = self.request.arguments.get("uname")
                        uname = uname[0]
			cmd = self.request.arguments.get("cmd")
			cmd = cmd[0]

                        try:
				db = sqlite3.connect('../DB.db')
                        	cursor = db.cursor()
				cursor.execute('''INSERT INTO sensors (sname,ip,path,uname,cmd)
                                		VALUES(?,?,?,?,?)''',(sname,ip,path,uname,cmd))
				sql = 'CREATE TABLE '+sname+'_disabled (sid INTEGER PRIMARY KEY)'		
				cursor.execute(sql)
				sql = 'CREATE TABLE '+sname+'_threshold (id INTEGER PRIMARY KEY, sid INTEGER, type TEXT, syntax TEXT, comment TEXT, sensor TEXT)'
				cursor.execute(sql)
				self.write(sname+' added! Refresh page to see changes.')
				db.commit()

			except StandardError,e:
                        	FILE = open('weberrorlog.txt','a')
                        	FILE.write('AddSensorHandler ERROR: '+str(e)+'\n')
                        	FILE.close()
				self.write(str(e))

                cursor.close()
                db.close()
			
class GetSensorsHandler(tornado.web.RequestHandler):
	def get(self):

               	db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

		sensors = []

		try:
			cursor.execute('SELECT * FROM sensors')
                	for row in cursor:
                        	sname,ip,path,uname,cmd = row
                        	check = "<center><input type='checkbox' name='sensorid' value='%s'></center>" % (sname)
				sensor = (check,sname,ip,path,uname,cmd)
                        	sensors.append(sensor)
		
		except StandardError,e:
			FILE = open('weberrorlog.txt','a')
			FILE.write('GetSensorsHandler ERROR: '+str(e)+'\n')
			FILE.close()

                cursor.close()
                db.close()
		self.write(json.dumps({"aaData":sensors},sort_keys=True,indent=4))

class GetRulesHandler(tornado.web.RequestHandler):
        def get(self):
                db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

		details = '<img class="sig" src="static/images/open.png">'
		sigs = []

                try:
                        cursor.execute('SELECT * FROM rules')
                        all_rules = cursor.fetchall()
                        cursor.execute('SELECT sname FROM sensors')
                        all_sensors = cursor.fetchall()

                	for row in all_rules:
                        	sidnr,revnr,source,ruleset,name,ref,date,rule = row
                        	status =''
                        	for hit in all_sensors:
                                	sql = 'SELECT sid FROM '+hit[0]+'_disabled WHERE sid='+str(sidnr)
                                        cursor.execute(sql)
                                        res = cursor.fetchone()
					sql = 'SELECT sid FROM %s_threshold WHERE sid="%s"' % (hit[0],sidnr)
					cursor.execute(sql)
					tmp2 = cursor.fetchone()
					if not (res is None):
						if not (tmp2 is None):
                                        		status = status+'<font class="red">'+hit[0]+'</font><font class="yellow"><b>!</b></font>&nbsp;' #red/yellow
						else:
							status = status+'<font class="red">'+hit[0]+'</font>&nbsp;' #red
                                	else:
						if not (tmp2 is None):
                                        		status = status+'<font class="green">'+hit[0]+'</font><font class="yellow"><b>!</b></font>&nbsp;' #green/yellow
						else:
							status = status+'<font class="green">'+hit[0]+'</font>&nbsp;' #green

                        	check = '<input type="checkbox" name="sidnr" value="%i">' % (sidnr)
                        	source_ruleset = '%s.%s' % (source,ruleset)
                        	sig = (check, sidnr, revnr, date, name, source_ruleset, ref, status, details)
                        	sigs.append(sig)

                except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('GetRulesetsHandler ERROR: '+str(e)+'\n')
                        FILE.close()

                cursor.close()
                db.close()
                self.write(json.dumps({"aaData":sigs},sort_keys=True,indent=4))

class GetRulesetsHandler(tornado.web.RequestHandler):
        def get(self):
                db = sqlite3.connect('../DB.db')
                cursor = db.cursor()

		rulesets = []
                
		try:
                        cursor.execute("SELECT DISTINCT ruleset_name, source_name FROM rules")
			query = cursor.fetchall()
                	
			for row in query:
                        	ruleset,source = row
                        	source_ruleset = '%s.%s' % (source,ruleset)
                        	check = '<center><input type="checkbox" name="rulesetid" value="%s"></center>' % (source_ruleset)
                        	sql = 'SELECT sidnr from rules WHERE source_name="%s" AND ruleset_name="%s"' % (source,ruleset)
                        	cursor.execute(sql)
                        	tmp = cursor.fetchall()
                        	count = len(tmp)
                        	sids = ','.join(str(x[0]) for x in tmp)
                        	cursor.execute('SELECT sname FROM sensors')
                        	all_sensors = cursor.fetchall()
                        	sql = 'SELECT MAX(date) FROM rules WHERE source_name="%s" AND ruleset_name="%s"' % (source,ruleset)
                        	cursor.execute(sql)
                        	max_date = cursor.fetchone()

                        	status = ''
                        	for x in all_sensors:
                                	sensor = x[0]
                                	sql = 'SELECT sid FROM %s_disabled WHERE sid IN ( %s )' % (sensor,sids)
                                	cursor.execute(sql)
                                	tmp2 = cursor.fetchall()
                                	scount = len(tmp2)
                                	if not (scount == count):
                                        	if not (scount == 0):
                                                	status = status+'<font class="green">%s</font><font class="red">%s</font>&nbsp;' % (sensor,scount)
                                        	else:
                                                	status = status+'<font class="green">%s</font>&nbsp;' % sensor
                                	else:
                                        	status = status+'<font class="red">%s</font>&nbsp;' % sensor

                        	rset = (check,source_ruleset,max_date,count,status)
                        	rulesets.append(rset)
		
		except StandardError,e:
                        FILE = open('weberrorlog.txt','a')
                        FILE.write('GetRulesetsHandler ERROR: '+str(e)+'\n')
                        FILE.close()		

                cursor.close()
                db.close()
                self.write(json.dumps({"aaData":rulesets},sort_keys=True,indent=4))

class ATuningHandler(tornado.web.RequestHandler):
        def get(self):
                self.render("atuning.html")

class ATuningHelpHandler(tornado.web.RequestHandler):
        def get(self):
                self.render("atuninghelp.html")

class SensorsHandler(tornado.web.RequestHandler):
        def get(self):
                self.render("sensors.html")

class RulesHandler(tornado.web.RequestHandler):
        def get(self):
                self.render("rules.html")

class RulesetsHandler(tornado.web.RequestHandler):
        def get(self):
                self.render("rulesets.html")

class MainHandler(tornado.web.RequestHandler):
        def get(self):
                self.render("index.html")
			
def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.autoreload.start()
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
