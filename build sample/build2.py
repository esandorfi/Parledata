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

#
# DATA SETTINGS
#
# 1/ disk source
#    where to load html dir on disk target (main_path_output)
main_path = "c:\\WWW-Git\\"
data_path = "py-eac\\data" # where to load data dir on disk source (main_path)
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
profile_path = "app\\eac"
main_path_output = "c:\\WWW-Parladata\\"
if( isProduction == 0 ):
    static_path = main_path_output + "local\\" + profile_path # put generated file in subdir local from static_path
else:
    static_path = main_path_output + profile_path


static_idx_path = static_path + "\\idx\\" 
static_th_path = "th\\" 

# 4/ update urls
root_url = main_url 
fw_url = main_url + main_assetsurl
if( profile_path != '' ):
    main_url += profile_path +"/" # update with subdir if defined
home_url = main_url 
static_url = main_url 

zen.logger.info("--- %s : %s" %(buildtype, main_url) )

# JOB
#
myZen = zen.PlwInit(input_path, profile_path, static_path,
        root_url, fw_url, static_url, template_path, data_path,
        static_idx_path, home_url, int(args.verbose))
myZen.stopIfError = True
myZen.profile("index.md")
#myZen.pushstatic("static")

# scan ( use --action media )
if args.action in (0, 'media'):
    myMedia = zen.PlwMedia()

    myMedia.scanimage("classe-msgs", input_path+"\\classe msgs", myZen.getstatic()+"classe-msgs", 2.5, 15, '.jpg', '@files', "scanimage.json")
    myMedia.scanimage("classe-ms", input_path+"\\classe ms", myZen.getstatic()+"classe-ms", 2.5, 15, '.jpg', '@files', "scanimage.json")
    myMedia.scanimage("classe-gs", input_path+"\\classe gs", myZen.getstatic()+"classe-gs", 2.5, 15, '.jpg', '@files', "scanimage.json")



# scan ( use --action template )
if args.action in (0, 'template'):





    myZen.route("classe-ms.md", "eac/print", "classe-ms-print")
    myZen.route("classe-msgs.md", "eac/print", "classe-msgs-print")
    myZen.route("classe-gs.md", "eac/print", "classe-gs-print")

    # INDEX HOME PAGE
    #myZen.pushstatic()
    myZen.route("index.md", "eac/page-simple", "index")



if myZen.noError == True:
    zen.logger.info("--- OK, IT IS DONE")
else:
    zen.logger.info("--- ERROR")











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