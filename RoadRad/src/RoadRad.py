#!/opt/local/bin/python
#This Python file uses the following encoding: utf-8


# This is the entry point to the script. Command line arguments are parsed here.
# Here the classes 'simulator' and 'configgenerator' are instantiated.

#expected format of the scene description file:
#<RoadScene>
#    <SceneDescription>
#        <Road  NumLanes="a number" LaneLength="a very large number" LaneWidth="width in meters" SidewalkWidth="width in meters"/>
#        <Background Context="City or Grass"/>
#    </SceneDescription>
#    <TargetParameters>
#        <!--<ViewPoint Distance="273" Height="1.2" TargetDistanceMode="fixedTargetDistance"/>-->
#        <ViewPoint Distance="distance in meters" Height="height in meters" TargetDistanceMode="fixedViewPoint or fixedTargetDistance"/>
#        <Target Size="edge length in meters" Reflectancy="RBG value" Position="right, left, or centre" OnLane="0-numlanes"/>
#    </TargetParameters>
#    <LDCs>
#        <!-- all LDC's come here, name of files and the light source type-->
#        <LDC Name="TX033306" LightSource="HPS"/>
#        <LDC Name="TX033307" LightSource="HPS"/>
#    </LDCs>    
#    <Poles>
#        <PoleArray PoleHeight="height in meters" PoleSpacing="spacing in meters" IsStaggered="True or false" LDC="name of ldc" Side="Right or left"/>
#        <PoleArray PoleHeight="height in meters" PoleSpacing="spacing in meters" IsStaggered="True or false" LDC="name of ldc" Side="Left or right"/>
#        <!--<PoleSingle PoleHeight="height in meters" LDC="name of ldc" PositionX="position along the road in meters" Side="Left or right"/>-->
#    </Poles>
#    <FocalLength FL="50"></FocalLength>
#</RoadScene>

#The description files itself must be placed in its own directory, and the name of the directory is to be
#passed to the script as a command line argument, with the option '--dir'. Inside this directory, must
#also be a direcotry called LDC, where all the ies files used int he scene must be kept

import os
from optparse import OptionParser
import sys
import shutil

import configGenerator
import simulator
import EnvVarSetter;


# Determine the current directory of executaion
# Important step because configfiles and output directories are relative to this path
def extractWorkingDir( ):
	currentDir = os.getcwd( )
	slashindex = currentDir.rfind("/" )
	currentDir = currentDir[ :slashindex ]
	return currentDir
        
def cleanSceneDir( path ):
	print "Will delete all created files in scene directory"
	cwd = extractWorkingDir()
	LMKSetMatDir = cwd + '/scenes/' + path + "/LMKSetMat"
	OctsDir = cwd + '/scenes/' + path + "/Octs"
	PicsDir = cwd + '/scenes/' + path + "/Pics"
	RadsDir = cwd + '/scenes/' + path + "/Rads"
	RefOctsDir = cwd + '/scenes/' + path + "/RefOcts"
	RefPicsDir = cwd + '/scenes/' + path + "/RefPics"
	LDCsDir = cwd + '/scenes/' + path + "/LDCs"
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
			if( file.endswith( ".dat" ) or file.endswith( ".rad" ) or file.endswith( ".txt" ) ):
				os.remove( LDCsDir + "/" + file )


				
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
	cleanSceneDir( options.cleanDir )	
	
elif( options.dir ):
	cleanSceneDir( options.dir )
	configGen = configGenerator.configGenerator( extractWorkingDir( ) + '/scenes/' + options.dir )
	sim = simulator.simulator( extractWorkingDir( ) + '/scenes/' + options.dir, options.skipRefPics )
    
else:
    oparser.print_usage( )


