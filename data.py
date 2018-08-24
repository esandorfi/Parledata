"""
Parladata
data.py
"""
# IMPORT
import sys
import os
import errno
import datetime
import logging
import re
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
import markdown2
import json
import csv
import yaml
from pprint import pprint

# parladata package
from .log import logger
from .scan import PlwScan
from .misc import plw_get_url, StringMetadata


# OBJECT PLWDATA
#	load
#	write
class PlwData(object):
	def __init__(self, objcfg, static_path):
		self.myTemplate = objcfg  # myTemplate object
		self.static_path = static_path


		self.idxcount = 0
		self.idx = {}
		self.myScan = PlwScan()


		self.jobending = []
		self.activedatafile = ''
		self.activedatadir = ''

	# LOAD
	#	data from argument
	def load(self, curdata):
		self.data = curdata
		#print(self.data)
		return True

	# LOAD_CSV
	#	data from csv file
	def load_csv(self, metakey, fdata):
		datafile = fdata
		if not os.path.exists(datafile):
			if( self.source_pathdata != '' ):
				if( self.source_pathdata[-1] != '\\' ):
					datafile = self.source_pathdata+'\\'+fdata
				else:
					datafile = self.source_pathdata+fdata
			if not os.path.exists(datafile):
				datafile = self.static_path+fdata
				if not os.path.exists(datafile):
					datafile = self.idxjson_path+fdata
					if not os.path.exists(datafile):
						logger.critical("skip csv file %s - doesn't exist in %s or in %s or in %s" %(fdata, self.source_pathdata, self.static_path, self.idxjson_path))
						return False

		logger.debug("load csv file "+ datafile)
		fcsv = open(datafile, 'r', encoding='utf-8')
		try:
			check_csvdelimiter = fcsv.readline()
			logger.debug("csv header : "+check_csvdelimiter)
			if( check_csvdelimiter.find(',') > -1 ):
				csvsep = ','
			else:
				csvsep = ';'
			logger.debug("csv delimiter is "+csvsep)
			fcsv.seek(0, 0)

			reader = csv.DictReader(fcsv, delimiter=csvsep)
		except ValueError as e:
			logger.critical("CSV ERROR "+str(e))
			return False

		tmplist = []
		try:
			for each in reader:
				#logger.debug(each)
				tmplist.append(each)
		except UnicodeDecodeError as e:
			logger.critical("CSV WRONG FORMAT - "+str(e))
			return False

		except:
			logger.critical("CSV WRONG FORMAT")
			raise

		self.idx[metakey] = tmplist
		self.idxcount += 1
		logger.debug("data dump [%s] %d:" %(metakey, self.idxcount))
		logger.debug(self.idx[metakey])
		return True

	# LOAD_YAML
	#	data from yaml file
	def load_yaml(self, metakey, fdata):
		datafile = fdata
		if not os.path.exists(datafile):
			if( self.source_pathdata != '' ):
				if( self.source_pathdata[-1] != '\\' ):
					datafile = self.source_pathdata+'\\'+fdata
				else:
					datafile = self.source_pathdata+fdata
			if not os.path.exists(datafile):
				datafile = self.static_path+fdata
				if not os.path.exists(datafile):
					datafile = self.idxjson_path+fdata
					if not os.path.exists(datafile):
						logger.critical("skip yaml file %s - doesn't exist in %s or in %s or in %s" %(fdata, self.source_pathdata, self.static_path, self.idxjson_path))
						return False
		logger.debug("load yaml file "+ datafile)
		fjson = open(datafile, 'r', encoding='utf-8')
		try:
			buf = list(yaml.load_all(fjson))
		except yaml.YAMLError as exc:
			logger.critical(str(exc))
			logger.critical("YAML ERROR in "+datafile)
			if hasattr(exc, 'problem_mark'):
				mark = exc.problem_mark
				logger.critical("YAML ERROR position: (%s:%s)" % (mark.line+1, mark.column+1))
			return False
		#import pdb; pdb.set_trace()
		self.idx[metakey] = buf
		self.idxcount += 1
		logger.debug("yaml dump [%s] %d:" %(metakey, self.idxcount))
		#pprint(self.idx[metakey])
		return True




	# LOAD_JSON
	#	data from json file
	def load_json(self, metakey, fdata):
		datafile = fdata
		if not os.path.exists(datafile):
			datafile = self.static_path+fdata
			if not os.path.exists(datafile):
				datafile = self.idxjson_path+fdata
				if not os.path.exists(datafile):
					logger.critical("skip json file %s - doesn't exist in %s or in %s " %(datafile, self.source_pathdata, self.static_path))
					return False
		logger.debug("load json file "+ datafile)
		fjson = open(datafile, 'r', encoding='utf-8')
		try:
			buf = json.load(fjson)
		except ValueError as e:
			logger.critical("JSON ERROR "+str(e))
			return False
		self.idx[metakey] = buf
		self.idxcount += 1
		logger.debug("json dump [%s] %d:" %(metakey, self.idxcount))
		#logger.debug(self.idx[metakey])
		#pprint(buf)
		return True

	# CHECK_METADATA
	#	ZENCSV 		load csv file
	#	ZENSCAN 	scan and load json
	def check_metadata(self, keyname, keydata, htmlmetadata):
		if keyname[:6] == 'zencsv':
			logger.debug("%s: %s" % (keyname, keydata))
			if keydata.find('.') == -1:
				logger.warning("META file doesn't have extension !")

			if( self.load_csv(keyname, keydata) == False ):
				return False

		elif keyname[:7] == 'zenscan':
			#if keydata.find('.') == -1:
			#	keydata += '.json'
			#import pdb; pdb.set_trace()
			try:
				scanname, scanfor, scanoption = keydata.split(' ')
			except:
				logger.critical("ZENSCAN has 3 arguments separated by space : [json filename generated] [extension to search] [options]")
				logger.critical("ZENSCAN: [FILETOCREATE.JSON] [.MD] [@ALL|@FILES]")
				logger.critical("zenscan: myscan .md @files")
				return False
			sourcedata = self.source_pathdata #htmlmetadata['sourceurl']
			logger.info("== %s: %s %s %s %s" % (keyname, scanname, scanfor, scanoption, sourcedata))
			if( self.zenscan(scanname, scanfor, scanoption, sourcedata) == False ):
				return False
			# check if job to do after processing this data
			if( scanoption.find('@build') == 0 ):
				if( self.source_pathdata == '' ):
					sourcedir = self.source_path
				else:
					sourcedir = self.source_pathdata
				self.jobending = [ sourcedir, scanname, scanfor, scanoption, sourcedata ]

		elif keyname[:8] == 'zenquery':
			if keydata.find('.') == -1:
				keydata += '.json'
			try:
				scanname, scanfor, scanoption = keydata.split(' ')
			except:
				logger.critical("ZENQUERY has 3 arguments separated by space : [json filename generated] [extension to search] [options]")
				logger.critical("ZENQUERY: [FILETOCREATE.JSON] [.MD] [@ALL|@FILES]")
				logger.critical("zenquery: myscan .md @files")
				return False
			sourcedata = self.source_pathdata #htmlmetadata['sourceurl']
			logger.info("== %s: %s %s %s %s" % (keyname, scanname, scanfor, scanoption, sourcedata))
			if( self.zenquery(scanname, scanfor, scanoption, sourcedata) == False ):
				return False
			# check if job to do after processing this data
			if( scanoption.find('@build') == 0 ):
				if( self.source_pathdata == '' ):
					sourcedir = self.source_path
				else:
					sourcedir = self.source_pathdata
				self.jobending = [ sourcedir, scanname, scanfor, scanoption, sourcedata ]


		elif keyname[:7] == 'zenyaml':
			if keydata.find('.') == -1:
				keydata += '.yaml'
			logger.info("== %s: %s" % (keyname, keydata))
			if( self.load_yaml(keyname, keydata) == False ):
				return False

		elif keyname[:7] == 'zenjson':
			if keydata.find('.') == -1:
				keydata += '.json'
			logger.info("== %s: %s" % (keyname, keydata))
			if( self.load_json(keyname, keydata) == False ):
				return False

		elif keyname[:6] == 'zenimg':
			if keydata.find('.') == -1:
				keydata += '.json'
			logger.info("== %s: %s" % (keyname, keydata))
			if( self.load_json(keyname, keydata) == False ):
				return False

		elif keyname[:11] == 'zentemplate' or keyname[:10] == 'zengabarit':
			if( self.template != '' ):
				#import pdb; pdb.set_trace()
				logger.debug("== TEMPLATE FORCE %s" % (self.template))
			else:
				logger.debug("== TEMPLATE %s: %s" % (keyname, keydata))
				self.template = keydata

		elif( keyname[:5] == 'image'):
			htmlmetadata[keyname] = re.sub(r"[^\w\\\\:.]", '-', keydata)
			logger.debug("== IMAGE translate :" + htmlmetadata[keyname])

		return True

	# ZENSCAN
	def zenscan(self, scanname, scanfor, scanoption, sourcedata):
		self.myScan.scanoption(self.static_path, self.static_url, self.source_path)
		self.myScan.activeurl(self.url[0])
		idxfilename = self.myScan.scan(sourcedata, scanfor, scanoption, self.idxjson_path+scanname)
		self.myScan.activeurl('')
		if idxfilename == '' :
			logger.critical("Error in idx generation with sourcedata "+sourcedata)
			return False
		return self.load_json("zenscan", idxfilename) # add multiple zenscan issue in future

	def zenquery(self, scanname, scanfor, scanoption, sourcedata):
		self.myScan.scanoption(self.static_path, self.static_url, self.source_path)
		self.myScan.activeurl(self.url[0])
		idxfilename = self.myScan.scan(sourcedata, scanfor, scanoption, self.idxjson_path+scanname, 1) #set as zenquery
		self.myScan.activeurl('')
		if idxfilename == '' :
			logger.critical("Error in idx generation with sourcedata "+sourcedata)
			return False
		return self.load_json("zenquery", idxfilename) # add multiple zenscan issue in future

	# LOAD_MARKDOWN
	#	data from markdown file
	def load_markdown(self, fdata, isprofile = False, otherfilename = '', ftemplate = ''):
		# reinitialize empty template for data
		self.template = ftemplate
		del self.jobending[:] # clear jobending list (used in zenscan @build option)
		self.activedatafile = fdata # data file to analyse

		# set data filepath
		#tmpsourceurl = fdata.partition('\\')[-1]
		tmpsourceurl = os.path.dirname(fdata)
		self.activedatadir = tmpsourceurl


		if( tmpsourceurl == '' ):
			self.source_pathdata = self.source_path
		else:
			self.source_pathdata = self.source_path+tmpsourceurl+'\\'
		datafile = self.source_path+fdata

		if os.path.exists(fdata):
			datafile = fdata
			self.source_pathdata = tmpsourceurl

		logger.debug("############################################")
		logger.debug("filename "+fdata)
		logger.debug("filename set as other : "+otherfilename)
		logger.debug("tmpsourceurl "+tmpsourceurl)
		logger.debug("source_pathdata "+self.source_pathdata)
		logger.debug("datafile "+datafile)

		self.url = plw_get_url(otherfilename if otherfilename != '' else fdata, self.static_path, self.static_url, self.source_path) # url, filename

		# verify if data metadata still in memory
		if self.idxcount > 0:
			self.idxcount = 0
			self.idx.clear()

		# load markdown
		logger.debug("load markdown file "+ datafile)
		if not os.path.exists(datafile):
			logger.critical("data file doesn't exist :"+datafile)
			return False
		htmlclass = {'table' : 'table is-hoverable'}
		#html = markdown2.markdown_path(datafile, extras=["header-ids", "metadata", "toc", "markdown-in-html", "tables"])
		if( datafile.find('.json') != -1 ):
			#with open(datafile) as json_file:
			#	json_data = json.load(json_file)
			html = StringMetadata(" ")
			#html.metadata = { 'filetype' : 'json', 'json' : json_data }
			html.metadata = { 'filetype' : 'json', 'zenjson' : datafile }
			logger.info("filetype is json")
		else:
			html = markdown2.markdown_path(datafile, extras={"metadata":None, "toc":None, "markdown-in-html":None, "tables":None, "html-classes":htmlclass})
		if not html:
			logger.info("error in markdown file :"+datafile)
			return False

		# add keywords
		html.metadata['content'] = html
		html.metadata['url'] = self.url[0]
		html.metadata['urldir'] = self.url[3]
		html.metadata['source'] = otherfilename if otherfilename != '' else fdata

		if isprofile == True:
			html.metadata['rooturl'] = self.root_url
			html.metadata['fwurl'] = self.fw_url
			html.metadata['homeurl'] = self.home_url
			html.metadata['mediaurl'] = self.media_url
			#html.metadata['sourcedata'] = self.source_data
			#html.metadata['sourceurl'] = self.content_path+"/"+tmpsourceurl + "/"
			html.metadata['staticurl'] = self.static_url
			html.metadata['webmaster'] = self.webmaster


		#logger.info("sourceurl : "+html.metadata['sourceurl'])
		#logger.info("staticurl : "+html.metadata['staticurl'])

		# check for metadata

		for keyname, keydata in html.metadata.items():
			if( self.check_metadata(keyname, keydata, html.metadata) == False ):
				return False

		# check for index
		if( self.idxcount > 0 ):
			logger.debug("number of index "+str(self.idxcount))
			for keyname, datavalue in self.idx.items():
				html.metadata[keyname] = datavalue
				#logger.debug(html.metadata[keyname])

		if( 'pagetitle' not in html.metadata ):
			p, f = os.path.split(html.metadata['source'])
			html.metadata['pagetitle'] = p


		# add profile
		if isprofile == False:
			html.metadata["profile"] = self.profile

		# put data in memory
		#logger.debug(html.metadata)
		self.load(html.metadata)
		return True

	def writejson(self, fout):
		try:
			myFile = open(fout, "w", encoding='utf-8')
		except FileNotFoundError as e:
			getdir = os.path.dirname(fout)
			logger.debug("create directory "+getdir+" from "+fout)
			try:
				os.makedirs(getdir, 0o777)
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise
			myFile = open(fout, "w", encoding='utf-8')


		try:
			json.dump(self.data, myFile, sort_keys=True,
                  indent=4, separators=(',', ': '))
		except ValueError as e:
			logger.critical("ERROR in json generation "+str(e))
		myFile.close()
		myFileinfo = os.stat(fout)
		logger.info("WRITE > %s : %d bytes" % (fout, myFileinfo.st_size))
		#import pdb; pdb.set_trace()


	# WRITE
	#	data from argument, template file, static file
	def write(self, curdata, curtemplate, curstatic='', isprofile = False):

		# print("curtemplate "+curtemplate+" static "+curstatic)
		# use template
		# 	check if curtemplate have '.', if not add '.html'
		# 	check if template is in list_templates() if not use index.html
		if( curtemplate == '' ):
			tmpfile = 'simple/page.html'

		elif( '.' in curtemplate ):
			tmpfile = curtemplate
		else:
			tmpfile = curtemplate + ".html"

		if( self.writehtml ):
			myTemplatefile = next((x for x in self.myTemplate.templates_env.list_templates() if x == tmpfile ), "")
			if myTemplatefile == '':
				logger.critical("template not found : "+tmpfile)
				return False
		else:
			myTemplatefile = tmpfile
		logger.debug("use template : "+myTemplatefile)

		# load data
		self.load(curdata)

		# check if javascript file
		if( '.js' in curstatic ):
			writeJson = False
		else:
			writeJson = True
		logger.debug("writeJson is "+str(writeJson)+" curstatic is "+curstatic)
		# write data
		# 	check if curstatic have '.', if not add '.html'
		#logger.info("DATA URL "+self.url[0]+" OUT "+self.url[1])



		if( '.' in curstatic ):
			#logger.info("1 "+curstatic)
			if( isprofile == True ):
				myStaticfile = self.idxjson_path+curstatic
			else:
				myStaticfile = self.static_path+curstatic
			myJsonfile = myStaticfile.rsplit('.', 1)[0]+".json"

			self.data['json'] = curstatic.rsplit('.', 1)[0]+".json"
		elif curstatic == '':
			myStaticfile = self.url[1]
			if( '.' in myStaticfile ):
				myJsonfile = myStaticfile.rsplit('.', 1)[0]+".json"
			else:
				myJsonfile = myStaticfile+".json"
			if( isprofile == True ):
				self.data['json'] = myJsonfile.replace(self.static_path, self.idxjson_path)
				myJsonfile = self.data['json']
			else:
				self.data['json'] = myJsonfile
			#logger.info("2 "+myJsonfile)
		else:
			#logger.info("3 "+curstatic)
			myStaticfile = self.static_path+curstatic + ".html"
			myJsonfile = self.static_path+curstatic + ".json"
			self.data['json'] = curstatic+".json"
		#logger.info("HTML FILE  "+myStaticfile)
		#logger.info("JSON FILE "+myJsonfile)


		if( isprofile == True ):
			#import pdb; pdb.set_trace()
			self.profile = self.data
			self.data = { "profile" : self.profile }
			logger.debug("initialize profile in json data")
			#pprint(self.profile)
			if writeJson is True:
				self.writejson(myJsonfile)
			return True

		# generate static html file from data and template
		if( self.writehtml ):
			try:
				myTemplate = self.myTemplate.templates_env.get_template(myTemplatefile)
				html = myTemplate.render(self.data)
				#print(html)
				try:
					myFile = open(myStaticfile, "w", encoding='utf-8')
				except FileNotFoundError as e:
					getdir = os.path.dirname(myStaticfile)
					logger.info("create directory "+getdir+" from "+myStaticfile)
					try:
						os.makedirs(getdir, 0o777)
					except OSError as e:
						if e.errno != errno.EEXIST:
							raise
					myFile = open(myStaticfile, "w", encoding='utf-8')
				myFile.write(html)
				myFile.close()
				myFileinfo = os.stat(myStaticfile)
				logger.info("WRITE > %s : %d bytes" % (myStaticfile, myFileinfo.st_size))

			except TemplateNotFound as e:
				logger.critical("ERROR JINJA template not found : "+str(e))
				return False

			except TemplateSyntaxError as e:
				logger.critical("ERROR JINJA template syntax error : "+str(e))
				#return False
				#continue jinja exception to get line number information
				raise
			except UndefinedError as e:
				logger.critical("ERROR JINJA variable not defined : "+str(e))
				raise
			except ValueError as e:
				logger.critical("ERROR in generate html "+str(e))
				return False

		# generate json data file
		if writeJson is True:
			self.writejson(myJsonfile)
		return True

	# CHECK IF JOB ENDING IS ON
	def ending(self, scanobj):
		if len(self.jobending) > 1:
			activedatafile = [ self.activedatafile, 'profile.md' ]
			activedatadir = self.activedatadir
			sourcedir = self.jobending[0]
			scanfor = self.jobending[2]
			i = 0
			del self.jobending[:]

			if( sourcedir == '' ):
				logger.info("JOBENDING ERROR - no sourcedir defined")
				return False

			logger.debug("#")
			logger.debug("#")
			logger.debug("# ENDING BUILD STARTED IN "+sourcedir+" FOR "+scanfor)


			logger.debug("active data file "+str(activedatafile))
			if( activedatadir == '' ):
				activedatadir = self.source_path
			logger.debug("active data dir "+activedatadir+" - source_path is "+self.source_path)
			#self.source_pathdata = self.source_path


			try:
				for dirnum, (dirpath, dirs, files) in enumerate(os.walk(sourcedir)):
					logger.debug("jobending find directory : " + dirpath+" original source path "+self.original_source_path)
					if( len(files) > 0 ):
						for filename in files:
							#import pdb; pdb.set_trace()
							if( filename not in activedatafile or dirpath != activedatadir ):
								if filename.rfind(scanfor) != -1:
									ftb = dirpath.split(self.original_source_path) # [1q]
									if len(ftb) > 1:
										filetobuild = ftb[1]
									else:
										filetobuild = ftb[0]
									if( len(filetobuild) > 0 and filetobuild[-1] != '\\'):
										filetobuild += '\\'
									filetobuild += filename
									if( True ): #filetobuild != activedatafile ):
										logger.debug("#")
										logger.debug("build : " + filetobuild)
										if not self.load_markdown(filetobuild):
											logger.critical("EMPTY DATA OR DATA WENT WRONG with "+filetobuild)
											return False
										if self.write(self.data, self.template) == False:
											return False
										scanobj.addidx(self.data)
										i += 1

			except Exception as e:
					logger.critical("error jobending walking dir : "+sourcedir+" "+str(e))
					return False
			logger.debug("JOBENDING ENDED with "+str(i)+" files")
		return True
