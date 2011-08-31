#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import os
from optparse import OptionParser

import configGenerator
import simulator

usage = "usage: %prog [options]"
version = "%prog 0.1"

oparser = OptionParser( )
oparser.add_option( "--skip-configs", action="store_true", dest="skipConfigs" )
oparser.add_option( "--skip-roads", action="store_true", dest="skipRoads" )
oparser.add_option( "--skip-dashed", action="store_true", dest="skipDashed" )
oparser.add_option( "--skip-solid", action="store_true", dest="skipSolid" )
oparser.add_option( "--skip-poles", action="store_true", dest="skipPoles" )
oparser.add_option( "--skip-lights", action="store_true", dest="skipLights" )
oparser.add_option( "--skip-luminaire", action="store_true", dest="skipLuminaire" )
oparser.add_option( "--skip-sky", action="store_true", dest="skipNightSky" )
oparser.add_option( "--skip-materials", action="store_true", dest="skipMaterials" )
oparser.add_option( "--skip-rview", action="store_true", dest="skipRView" )
oparser.add_option( "--skip-targets", action="store_true", dest="skipTargets" )
oparser.add_option( "--skip-target", action="store_true", dest="skipTarget" )

( options, args ) = oparser.parse_args()

if( not options.skipConfigs ):
    configGen = configGenerator.configGenerator( os.getcwd( ) )
    
    if( not options.skipRoads ):
        configGen.parseRoads( )
    
    if( not options.skipDashed ):
        configGen.printDashedWhiteRad( )
    
    if( not options.skipSolid ):
        configGen.printSolidYellowRad( )
    
    if( not options.skipPoles ):
        configGen.parsePoles( )
    
    if( not options.skipLights ):
        configGen.printLightsRad( )
    
    if( not options.skipLuminaire ):
        configGen.printLuminaireRad( )
    
    if( not options.skipNightSky ):
        configGen.printNightSky( )
        
    if( not options.skipMaterials ):
        configGen.printMaterialsRad( )
    
    if( not options.skipRView ):
        configGen.printRView( )
    
    if( not options.skipTargets ):
        configGen.printTargets( )
    
    if( not options.skipTarget ):
        configGen.printTarget( )
    
sim = simulator.simulator( os.getcwd( ) )
    
