"""
Parladata
init.py
"""

# IMPORT
import sys
import os
from datetime import datetime


from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
import markdown2
import json
import csv
from pprint import pprint


# parladata global string
verPackage = "parledata"

# parladata package
from parledata.log import logger, loglevel
from .template import PlwTemplate
from .data import PlwData
from .scan import PlwScan

from logging import DEBUG, CRITICAL, INFO
# GLOBAL VARIABLES
# info

WEBMASTER = 'Parledata from Parle Web'

# return dict values
def get_v(data, *args):
	if args and data:
		element  = args[0]
		if element:
			value = data.get(element)
			return value if len(args) == 1 else get_v(value, *args[1:])


# OBJECT PlwInit
#	Use as container for configuration
#	Use as route commands
#
# 	object defined
#		myTemplate (PlwTemplate), myData (PlwData)
#	variables defined
#		stopIfError, noError - route function return
#		static - static output path
#	functions
#		__init__, route, pushstatic
#
class PlwInit(object):
	# INIT
	# SET DEFAULT URLS AND PATH
	def __init__(self, *args):
		# set datetime
		self.dtstart = datetime.now()
		self.stopIfError = True
		self.noError = True
		self.isInit = False
		self.history = []



	def initload(self, config):
		# loglevel
		#loglevel(fdebug)

		# replace url
		root_url = config['build']['root_url'].replace('\\', '/')
		fw_url = config['build']['fw_url'].replace('\\', '/')
		static_url = config['build']['static_url'].replace('\\', '/')
		home_url = config['build']['home_url'].replace('\\', '/')



		# init plwtemplate object (jinja)
		self.myTemplate = PlwTemplate(config['build']['template_path'], config['build']['static_path'])

		# init PlwData (data content to html/json)
		self.myData = PlwData(self.myTemplate)

		# init PlwScan (index content)
		self.myScan = PlwScan(config['build']['static_idx_path'])

		# dict for index generated from plwidx.scan call,
		# used after in plwdata as { idxname : json full pathname }
		self.myData.idxjson = {}

		# directories for geting data and creating html
		# and be sure static has end \
		if not config['build']['source_path'][-1] == '\\':
			config['build']['source_path'] = config['build']['source_path'] + '\\'
		self.static = config['build']['static_path']
		self.myData.home_url = config['build']['home_url']
		self.myData.source_path = config['build']['source_path']
		self.myData.original_source_path = config['build']['source_path']
		self.original_source_path = config['build']['source_path']
		self.myData.source_data = config['build']['profile_path']
		self.myData.content_path = config['build']['data_path']
		# path in static dir where idx json files are generated
		self.myData.idxjson_path = config['build']['static_idx_path']

		# url defined for jinja templates
		self.myData.root_url = config['build']['root_url']
		self.myData.fw_url = config['build']['fw_url']
		self.myData.static_url = config['build']['static_url']
		self.myData.profile = {}
		self.static_url = config['build']['static_url']

		# webmaster string in jinja head
		self.myData.webmaster = config['build']['webmaster']

		# stop build if errors
		self.stopIfError = True
		self.noError = True
		self.sharedprofile = {}
		"""
		# log variables
		logger.debug("ZEN PlwInit - Input arguments")
		logger.debug("source_path "+source_path+" (known as source_path)")
		logger.debug("profile_path "+profile_path+" (known as source_data)")
		logger.debug("static_path "+static_path+" (known as static)")
		logger.debug("root_url "+root_url)
		logger.debug("fw_url "+fw_url)
		logger.debug("static_url "+static_url)
		logger.debug("template_path "+template_path)
		logger.debug("data_path "+data_path+ " (known as content_path)")
		logger.debug("static_idx_path "+static_idx_path +" (known as idxjson_path)")
		logger.debug("home_url "+home_url)
		"""
		# init loaded
		self.isInit = True

	#def __del__(self):
	def end(self):
		#import pdb; pdb.set_trace()
		dtend = datetime.now()
		d = dtend - self.dtstart
		logger.info("--- %s end in %s seconds" %("OK" if self.noError == True else "---- ERROR", d))
		if self.noError == True:
			logger.info("--- OK, IT IS DONE")
		else:
			logger.info("--- ERROR")

	def clearhistory(self):
		del self.history
		self.history = []

	def sethistory(self, history, type = INFO):
		if( type == DEBUG ):
			msg = "+ "
			logger.debug(history)
		elif( type == CRITICAL ):
			msg = "!!!!!!!! "
			logger.critical(history)
		else:
			msg = ""
			logger.info(history)
		if( not self.history ):
			self.history = []
		self.history.append(msg+history)

	def gethistory(self):
		if( self.history ):
			msg = '<br>'.join(self.history)
		else:
			msg = " build did nothing "
		return msg

	# IDX
	def openidx(self, name):
		return self.myScan.openidx(name)
	def closeidx(self):
		return self.myScan.closeidx()

	# ROUTE
	# GENERATE HTML FILE
	def route(self, fdata, ftemplate = '', fhtml = '', isprofile = False, isjobending = True):
		if self.isInit == False:
			self.sethistory("No configuration loaded", CRITICAL)
			return False

		if self.stopIfError is True and self.noError is False:
			self.sethistory("Previous error - skip next file : "+fhtml, CRITICAL)

			return False
		if not self.myTemplate.is_valid():
			self.sethistory("PlwTemplate is not set", CRITICAL)
			return False


		# WRITE STATIC WITH DATA AND TEMPLATE
		if not self.myData.load_markdown(fdata, isprofile, fhtml):
			self.sethistory("EMPTY DATA OR DATA WENT WRONG", CRITICAL)
			self.noError = False
			return False
		#import pdb; pdb.set_trace()
		if ftemplate == '' and self.myData.template != '':
			ftemplate = self.myData.template
		if isprofile == True:
			self.myData.profile = {}
		if isjobending == True:
			self.noError = self.myData.write(self.myData.data, ftemplate, fhtml, isprofile)

		#if( self.noError == True)
		#	self.noError = self.myScan.addidx(self.myData.data)
		if( self.noError == True):
			if( isprofile == True ):
				self.sharedprofile = self.myData.data
				self.sethistory("Initialize shared profile from "+fdata)
			if( isjobending == True ):
				if( self.myData.url ):
					self.sethistory(fdata +" + " +ftemplate +"-> "+self.myData.url[0])
				self.noError = self.myData.ending()

		return self.noError

	# CHANGE DATA PATH
	def sourcepath(self, sou = ''):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False

		if( sou == '' ):
			sou = self.original_source_path
		self.myData.source_path = sou
		if not self.myData.source_path.endswith('\\'):
			self.myData.source_path = self.myData.source_path + '\\'
		logger.info("#")
		logger.info("# source_path : "+self.myData.source_path)

	# PUSH STATIC
	# 	ADD SUBFOLDER TO STATIC PATH
	#	set variable PWLTEMPLATE static_path
	#	if changecomplete, apply fullpathname, instead relative from PWLINIT
	def pushstatic(self, ffolder = '', fchangecomplete = 0):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False

		#import pdb; pdb.set_trace()

		if self.stopIfError is True and self.noError is False:
			return False
		if ffolder == '':
			tmppath=self.static
		else:
			if( fchangecomplete == 1 ):
				tmppath = ffolder;
			else:
				if( self.static[-1] != '\\' ):
					tmppath = self.static+"\\"+ffolder
				else:
					tmppath = self.static + ffolder
		#no need ## self.myData.static_url = self.static_url +ffolder+"/"
		self.myTemplate.set_staticpath(tmppath)
		self.myData.static_path = self.myTemplate.static_path

	def getstatic(self):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False

		return self.myTemplate.static_path

	# PROFILE
	#	SET SHARED COMMUN INFORMATION FROM A SPECIFIC FILE
	def profile(self, fdata):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False


		if self.stopIfError is True and self.noError is False:
			return False
		logger.debug("# load commun profile file : "+fdata)
		self.route(fdata, 'console/profile', '', True)

	# ADDIDX
	#	ADDIDX
	def addidx(self, idxname, idxpath):
		if self.isInit == False:
			logger.critical("No configuration loaded")
			return False

		self.myData.idxjson[idxname] = idxpath;
		logger.debug("add idx [%s] from %s" %(idxname, idxpath))
