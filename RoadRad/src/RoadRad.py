#This Python file uses the following encoding: utf-8

import os
from optparse import OptionParser
import sys

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
oparser.add_option( "--refPic", action ="store_true", dest = "refPic" )

( options, args ) = oparser.parse_args()

if( options.setEnv ):
    envtest = EnvVarSetter.EnvVarSetter( options.setEnv )
    if( not envtest.testRadianceInstall( ) ):
            print "Radiance not installed properly. Adding path"
            envtest.addRadianceEnv()
            sys.exit()

if( options.dir ):
    configGen = configGenerator.configGenerator( extractWorkingDir( ) + '/scenes/' + options.dir )
    sim = simulator.simulator( extractWorkingDir( ) + '/scenes/' + options.dir, options.refPic )
else:
    oparser.print_usage( )


