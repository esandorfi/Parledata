"""
Parladata
misc.py
"""
import re
import os
import logging

from selenium import webdriver
from .log import logger

# URLIFY
#	transform string to url

def plw_urlify(s):
	s = re.sub(r"[^\w]", '-', s)
	# Replace all runs of whitespace with a single dash
	#s = re.sub(r"\s+", '-', s)
	return s

# STRING METADATA FOR SIMULATE MARKDOWN
#

class StringMetadata(str):
	metadata = None


# GET URL
#	input:
#	from sourcefile
#	where has to be created in static path
# 	what is the url to static root
#
#	output: (list)
#	url
#	full filename
def plw_get_url(sourcefile, static_path='', static_url='', source_path=''):
	#import pdb; pdb.set_trace()
	logger.debug("# geturl source file %s path %s, static url %s path %s" %(sourcefile, source_path, static_url, static_path) )

	sourcefile = sourcefile.lower()
	# remove extension
	if sourcefile.find('.'):
		if sourcefile.find('.md') != -1:
			filename = sourcefile.split('.')[0]+'.html'
			logger.debug("find md")
		else:
			filename = sourcefile
	else:
		filename = sourcefile+'.html'

	logger.debug("filename is "+filename)

	# remove source_path if any
	if source_path != '':
		source_path = source_path.lower()
		n = filename.find(source_path)
		#logger.info('n '+str(n)+' source '+source_path)
		if n == 0:
			filename = filename[len(source_path):]
	## has to check
	if os.path.exists(filename):
		fullfilename = filename
	else:
		fullfilename = static_path+filename
	logger.debug("static file: "+fullfilename)

	path = os.path.dirname(fullfilename)
	if not os.path.exists(path):
		logger.debug("path does not exist : "+path)
	#else:
	#	logger.info("PATH IS "+path)

	# check if index
	if sourcefile.find('index'):
		filename = filename.split('index')[0]

	if( filename.find(source_path) != -1 ):
		logger.info(filename+" "+source_path + " len "+str(len(source_path)))
		filename = filename[len(source_path):]
		logger.info(" filename now just is "+filename)

	url = (static_url + filename).replace('\\', '/')
	logger.debug("url: "+url)
	return [ url, fullfilename ]


# PlwWeb
#   use selenium browser object with Firefox

class PlwWeb(object):
	def __init__(self):
		self.browser = webdriver.Firefox()

	def __del__(self):
		self.browser.close()

	def screenshot(self, server, url, dirtosave, dir_th_url):
		self.browser.get(server+url)
		imgname = plw_urlify(url)
		imgname += ".png"
		urlimgname = (dir_th_url+imgname).replace('\\', '/')
		fullimgname = dirtosave+imgname
		if( dirtosave != '' and os.path.exists(dirtosave) == False ):
			os.makedirs(dirtosave, 0o777)

		self.browser.save_screenshot(fullimgname)
		logger.info("save screenshot to fullimgname "+fullimgname +" url "+urlimgname)
		return urlimgname
