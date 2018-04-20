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
zen.logger.info("--- BUILD SCAN")
isProduction = 0
args = zen.args()
if args.verbose == '1':
    zen.loglevel(1)
zen.loglevel(1)
#
# DATA SETTINGS
#
#
# DATA SETTINGS
#
# 1/ disk source
#    where to load html dir on disk target (main_path_output)
main_path = "c:\\WWW-Git\\"
data_path = "parladata.template" # where to load data dir on disk source (main_path)
input_path = main_path + data_path
template_path = main_path + "parladata.template"

# 2/ url server local
main_localurl = "http://parladata.l/"
main_produrl = "/"
main_assetsurl = "assets/"
if isProduction == 0:
    buildtype = "LOCAL"
    main_url = main_localurl    
else:
    buildtype = "PRODUCTION"
    main_url = main_produrl 

# 3/ disk target 
profile_path = "parladata"
main_path_output = "c:\\WWW-Parladata\\"
if( isProduction == 0 ):
    static_path = main_path_output + "local\\" + profile_path # put generated file in subdir local from static_path
else:
    static_path = main_path_output + profile_path


static_idx_path = static_path + "\\idx\\" 
static_th_path = static_path + "\\th\\" 

# 4/ update urls
root_url = main_url 
fw_url = main_url + main_assetsurl
if( profile_path != '' ):
    main_url += profile_path +"/" # update with subdir if defined
    if( isProduction == 0 ):
        th_url = "local/"+profile_path +"/th/"
    else:
        th_url = profile_path +"/th/"
else:
    th_url = "/th/"
home_url = main_url 
static_url = main_url 

"""

# 1/ instance
#    where to put html dir on disk target (main_path_output)
profile_path = "parladata"

# 2/ disk source 
main_path = "c:\\WWW-Git\\"
data_path = "parladata.template" # where to load data dir on disk source (main_path)
input_path = main_path + "\\" + data_path
template_path = main_path + "\\parladata.template"

# 3/ url server local
main_localurl = "http://parladata.l/"
main_produrl = "/"
main_assetsurl = "assets"

if isProduction == 0:
    buildtype = "LOCAL"
    main_url = main_localurl    
else:
    buildtype = "PRODUCTION"
    main_url = main_produrl 

# 4/ disk target 
main_path_output = "c:\\WWW-Parladata\\"
static_path = main_path_output + profile_path
if( isProduction == 0 ):
    static_path += "\\local" # put generated file in subdir local from static_path
static_idx_path = static_path + "\\idx\\" 
static_th_path = "local\\th\\" 

# 5/ update urls
if( profile_path != '' ):
    main_url += profile_path +"/" # update with subdir if defined

root_url = main_url 
fw_url = main_url + main_assetsurl
home_url = main_url 
static_url = main_url 
"""
zen.logger.info("--- %s : %s" %(buildtype, main_url) )

# JOB
#
# Scan ( use --action scan )
if args.action in (0, 'scan'):
    myIdx = zen.PlwScan(static_idx_path) # where to put idx generated

    myIdx.scanoption(main_path_output, "http://parladata.l/", main_path_output, static_th_path, th_url)
    #idxfilename = myIdx.scan("py-compagnie\\local", ".html", "@SCREENSHOT", static_idx_path+"idx-compagnie.json")
    idxfilename = myIdx.scan(main_path_output+"local\\app\\eac", ".html", "@SCREENSHOT", static_idx_path+"idx-eac.json")
    if( idxfilename == ''):
        zen.logger.critical("Error in idx generation")
        sys.exit(1)
    else:
        zen.logger.info("scan generated as "+idxfilename)
"""
    idxfilename = myIdx.scan("parladata.template", ".html", "@SCREENSHOT", static_idx_path+"idx-parladata-template.json")
    if( idxfilename == ''):
        zen.logger.critical("Error in idx generation")
        sys.exit(1)
"""
# scan ( use --action template )
if args.action in (0, 'template'):
    myZen = zen.PlwInit(input_path, profile_path, static_path,
            root_url, fw_url, static_url, template_path, data_path,
            static_idx_path, home_url, int(args.verbose))
    myZen.stopIfError = True
    myZen.profile("profile.md")
    myZen.route("index.md", "iuadmin-idx", "index")
    myZen.route(idxfilename, "iuadmin-idx", "eac")

#myZen.addidx(thisidx, idxfilename)
    
#del myIdx


"""
myZen.route("abonnés\\index.md", "cie/page-simple")
myZen.route("mdp\\index.md", "page-parladata")
myZen.route("vitrine\\index.md", "cie/page-sitemap")
myZen.route("vitrine\\art de dire\\formation\\lire a haute voix\\index.md", "cie/page-formation-v2")
myZen.route("vitrine\\art de dire\\formation\\prendre la parole en public\\index.md", "cie/page-formation-v2")
myZen.route("vitrine\\art de dire\\formation\\web\\index.md", "cie/page-formation-v2")
myZen.route("profile\\profile.md", "page-simple")

# INDEX HOME PAGE
myZen.pushstatic()
myZen.route("profile\\index.md", "cie/page-simple", "index")

if myZen.noError == True:
    zen.logger.info("--- OK, IT IS DONE")
else:
    zen.logger.info("--- ERROR")
"""