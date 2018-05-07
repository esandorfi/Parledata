# BUILD SCAN FOR SCREENSHOT

import sys, os, argparse

enginepath = "c:\\WWW-Git\\python";
sys.path.append(enginepath)
try:
	import parladata as zen
except ModuleNotFoundError as e:
	print("MODULE NOT FOUND "+str(e))

#
# MAIN
#
args = zen.args()
if args.verbose == '1':
	zen.loglevel(1)

# JOB

profile = 'cienpinot'
myConfig = zen.PlwConfig(profile)
if( myConfig.config is None ):
	zen.logger.critical("No configuration "+profile)
	sys.exit(1)

myZen = zen.PlwInit()
myZen.initload(myConfig.config)


# SHARED PROFILE
myZen.profile("profile.md")
#myZen.pushstatic("data")

# INDEX
#myIdx = zen.PlwIdx(static_idx_path, myZen)
myIdx = zen.PlwScan(myConfig.config['build']['static_idx_path'], myConfig.config['build']['source_path'])
"""
if args.action in (0, 'scan'):
	thisidx = "data-index-formation.json"
	idxfilename = myIdx.scan(myConfig.config['build']['source_path']+"formation", ".md", '@none', thisidx)
	if( idxfilename == ''):
		zen.logger.critical("Error in idx generation")
		sys.exit(1)
	myZen.addidx(thisidx, idxfilename)
	#myZen.route("formation\\index.md", "iuadmin-idx", "zen\\formation")
"""

if args.action in (0, 'console'):
	# profile
	myZen.profile("console\\profile.md")
	# pages
	myZen.route("console\\abonnes\\index.md")
	myZen.route("console\\mdp\\index.md")
	myZen.route("console\\calendrier\\index.md")
	myZen.route("console\\plan\\index.md")
	# home
	myZen.route("console\\index.md")

if args.action in (0, 'formation'):
	myZen.route("formation\\art de dire\\0 index.md")
	myZen.route("formation\\parle web\\0 index.md")
	myZen.route("formation\\index.md")

if args.action in ('f1'):
	myZen.route("formation\\art de dire\\0 index.md")

if args.action in ('f2'):
	myZen.route("formation\\parle web\\0 index.md")

if args.action in ('f3'):
	myZen.route("formation\\index.md")



if args.action in (0, 'vitrine'):
	myZen.route("vitrine\\index.md")
	myZen.route("profile.md", "landingv3", "index")


	#myZen.route("vitrine\\art de dire\\formation\\lire a haute voix\\index.md", "cie/page-formation-v2")
	#myZen.route("vitrine\\art de dire\\formation\\prendre la parole en public\\index.md", "cie/page-formation-v2")
	#myZen.route("vitrine\\art de dire\\formation\\web\\index.md", "cie/page-formation-v2")
	#myZen.route("profile\\profile.md", "page-simple")

	# INDEX HOME PAGE
	#myZen.pushstatic()



myZen.end()
