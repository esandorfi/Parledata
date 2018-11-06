# BUILD SCAN FOR SCREENSHOT
# -*-coding:utf-8 -*-
"""
Build individual script - run from command line

"""

import sys, os, argparse

#enginepath = "c:\\www-parledata";
#sys.path.append(enginepath)


try:
	import parledata as zen
except ModuleNotFoundError as e:
	print("MODULE NOT FOUND "+str(e))
	sys.exit(1)

profile = 'pld'

args = zen.args()
myConfig = zen.PlwConfig(profile)
if args.verbose == '1':
	zen.loglevel(1)
if( myConfig.config is None ):
	sys.exit(1)

myZen = zen.PlwInit()
myZen.initload(myConfig.config)

if(args.source):
	for f in args.source:
		myZen.route(f)

myZen.end()
