"""
Parladata
log.py
"""

import logging
from .init import verPackage
global logger


def loginit(fdebug = 0, fname = ''):
	print("LOGINIT as "+str(fdebug))
	if( fname == ''):
		fname = verPackage
	flevel = logging.INFO if fdebug == 0 else logging.DEBUG


	logging.basicConfig(format='%(filename)s:%(lineno)-4d %(levelname)-6s %(message)s',
    	datefmt='%d-%m-%Y:%H:%M:%S',
    	level=flevel)
	#logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)-4d %(levelname)-6s %(message)s',
    #	datefmt='%d-%m-%Y:%H:%M:%S',
    #	level=flevel)



	#logging.basicConfig(format='%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d %(message)s', datefmt='%d-%m-%Y:%H:%M:%S', level=flevel)
	logger = logging.getLogger(fname)
	fh = logging.FileHandler(verPackage+'.log')
	#fh.setlevel(logging.DEBUG)

	#ch = logging.StreamHandler()
	#logger.addHandler(fh)
	logger.addHandler(fh)
	return logger

def loglevel(fdebug = 0):
	flevel = logging.INFO if fdebug == 0 else logging.DEBUG
	logger.setLevel(flevel)
	logger.info("set level to "+str(flevel))


logger = loginit()
