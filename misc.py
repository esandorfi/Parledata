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
def plw_get_url(sourcefile, static_path='', static_url='', source_path=''):

	#import pdb; pdb.set_trace()

	logger.info("# source file: "+sourcefile)
	logger.info("# source path: "+source_path)
	logger.info("# static path: "+static_path)



	# remove extension
	if sourcefile.find('.'):
		if sourcefile.find('.md'):
			filename = sourcefile.split('.')[0]+'.html'
		else:
			filename = sourcefile
	else:
		filename = sourcefile+'.html'

	# remove source_path if any
	if source_path != '':
		n = filename.find(source_path)
		#logger.info('n '+str(n)+' source '+source_path)
		if n == 0:
			filename = filename[len(source_path):]



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
	logger.info("url: "+url)
	return [ url, fullfilename ]
