#!/opt/local/bin/python
#This Python file uses the following encoding: utf-8
#asd
import os
from optparse import OptionParser
import sys
import shutil

import configGenerator
import simulator
import EnvVarSetter;

def extractWorkingDir( ):
        currentDir = os.getcwd( )
        slashindex = currentDir.rfind("/" )
        currentDir = currentDir[ :slashindex ]
        return currentDir

usage = "usage: %prog [options]"
version = "%prog 0.1"

oparser = OptionParser( )
oparser.add_option( "--setEnv", action="store", type="string", dest="setEnv" )
oparser.add_option( "--dir", action ="store", type = "string", dest = "dir" )
oparser.add_option( "--skipRefPics", action ="store_true", dest = "skipRefPics" )
oparser.add_option( "--cleanDir", action ="store", type="string", dest = "cleanDir" )

( options, args ) = oparser.parse_args()

if( options.setEnv ):
    envtest = EnvVarSetter.EnvVarSetter( options.setEnv )
    if( not envtest.testRadianceInstall( ) ):
            print "Radiance not installed properly. Adding path"
            envtest.addRadianceEnv()
            sys.exit()

if( options.cleanDir ):
	print "Will delete all created files in scene directory"
	cwd = extractWorkingDir()
	LMKSetMatDir = cwd + '/scenes/' + options.cleanDir + "/LMKSetMat"
	OctsDir = cwd + '/scenes/' + options.cleanDir + "/Octs"
	PicsDir = cwd + '/scenes/' + options.cleanDir + "/Pics"
	RadsDir = cwd + '/scenes/' + options.cleanDir + "/Rads"
	RefOctsDir = cwd + '/scenes/' + options.cleanDir + "/RefOcts"
	RefPicsDir = cwd + '/scenes/' + options.cleanDir + "/RefPics"
	LDCsDir = cwd + '/scenes/' + options.cleanDir + "/LDCs"
	if( os.path.exists( LMKSetMatDir ) ):
		shutil.rmtree( LMKSetMatDir )
	if( os.path.exists( OctsDir ) ):
		shutil.rmtree( OctsDir )
	if( os.path.exists( PicsDir ) ):
		shutil.rmtree( PicsDir )
	if( os.path.exists( RadsDir ) ):
		shutil.rmtree( RadsDir )
	if( os.path.exists( RefOctsDir ) ):
		shutil.rmtree( RefOctsDir )
	if( os.path.exists( RefPicsDir ) ):
		shutil.rmtree( RefPicsDir )
	if( os.path.exists( LDCsDir ) ):
		dirList = os.listdir( LDCsDir )
		for file in dirList:
			if( file.endswith( ".dat" ) or file.endswith( ".rad" ) ):
				os.remove( LDCsDir + "/" + file )			
	
elif( options.dir ):
    configGen = configGenerator.configGenerator( extractWorkingDir( ) + '/scenes/' + options.dir )
    sim = simulator.simulator( extractWorkingDir( ) + '/scenes/' + options.dir, options.skipRefPics )
    
else:
    oparser.print_usage( )


