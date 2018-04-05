"""
Parladata
misc.py
"""
import os
import logging
from .log import logger

# GET URL
#	input:
#	from sourcefile
#	where has to be created in static path
# 	what is the url to static root
#
#	output: (list)
#	url
#	full filename
def plw_get_url(sourcefile, static_path='', static_url=''):
	logger.info("SOURCE FILE IS "+sourcefile)
	# remove extension
	if sourcefile.find('.'):
		filename = sourcefile.split('.')[0]+'.html'
	else:
		filename = sourcefile+'.html'
	fullfilename = static_path+filename
	logger.info("FULL FILENAME IN STATIC PATH IS "+fullfilename)

	path = os.path.dirname(fullfilename)
	if not os.path.exists(path):
		logger.info("PATH DOES NOT EXIST "+path)
	else:
		logger.info("PATH IS "+path)

	# check if index
	if sourcefile.find('index'):
		filename = filename.split('index')[0]

	url = (static_url + filename).replace('\\', '/')
	logger.info("SOURCE URL IS "+url)
	return [ url, fullfilename ]
