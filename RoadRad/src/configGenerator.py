# This Python file uses the following encoding: utf-8

import os
import sys
from xml.dom.minidom import parse

class configGenerator:
    
    def __init__( self, workingDir ):
        #retrieve working directory info
        self.rootDirPath = workingDir
        self.xmlConfigsPath = self.rootDirPath + '/configs/'
        
        self.sceneDirPrefix = '/scene'
        
        self.roadFileName = 'road.xml'
        self.poleFileName = 'poles.xml'
        
        self.sceneLengths = [ ]
        self.pavementWidths = [ ]
        self.sidewalkWidths = [ ]
        self.grassWidths = [ ]
        self.numLanes = [ ]
        
        self.poleHeight = [ ]
        self.isStaggered = [ ]
        self.poleSpacing = [ ]
        
        self.parseAll( )
    
    def parseAll( self ):
        print 'Working Directory: ' + self.rootDirPath
        print 'Attempting to locate XML config files in: ' + self.xmlConfigsPath
        
        if( not os.path.isdir( self.xmlConfigsPath ) ):
            print 'Config directory not found in the working directory, Quitting'
            return False
        
        if( not os.path.isfile( self.xmlConfigsPath + self.roadFileName ) ):
            print 'No road definition found, Quitting'
            return False
        
        print 'Attempting to parse road scenes'
        if( not self.parseRoadScenes( self.xmlConfigsPath + self.roadFileName ) ):
            print 'Error parsing road.xml, check syntax'
            return False
        
        print 'Attempting to parse pole configs'
        if( not self.parsePoleConfigs( self.xmlConfigsPath + self.poleFileName ) ):
            print 'Error parsing road.xml, check syntax'
            return False
        
        self.printRads( )
        
        return True
    
    def parseRoadScenes( self, path ):
        file = open( path, 'r' )
        dom = parse( file )
        file.close( )
        
        scenesList = dom.getElementsByTagName( 'Scenes' )
        
        for scene in scenesList:
            for child in scene.childNodes:
                if( child.attributes ):
                    self.sceneLengths.append( int( child.attributes[ "PavementLength" ].value ) )
                    self.pavementWidths.append( int( child.attributes[ "PavementWidth" ].value ) )
                    self.sidewalkWidths.append( int( child.attributes[ "SidewalkWidth" ].value ) )
                    self.grassWidths.append( int( child.attributes[ "GrassfieldWidth" ].value ) )
                    self.numLanes.append( int( child.attributes[ "NumLanes" ].value ) )
        
        print 'Successfully parsed ' + str( len( self.sceneLengths ) ) + ' scenes.'
        
        return True
    
    def parsePoleConfigs( self, path ):
            file = open( path, 'r' )
            dom = parse( file )
            file.close( )
        
            polesList = dom.getElementsByTagName( 'Poles' )
        
            for pole in polesList:
                for child in pole.childNodes:
                    if( child.attributes ):
                        self.poleHeight.append( int( child.attributes[ "PoleHeight" ].value ) )
                        self.poleSpacing.append( int( child.attributes[ "PoleSpacing" ].value ) )
                        self.isStaggered.append( bool( child.attributes[ "IsStaggered" ].value ) )
        
            print 'Successfully parsed ' + str( len( self.poleHeight ) ) + ' pole configs.'
            return True
    
    def printRads( self ):
        
        for i in range( 0, len( self.sceneLengths ) ):
            
            if( not os.path.isdir( self.rootDirPath + self.sceneDirPrefix + str( i ) ) ):
                os.mkdir( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            
            f = open( self.rootDirPath + self.sceneDirPrefix + str( i ) + '/road.rad', "w" )
    
            f.write( '######road.rad######\npavement polygon pave_surf\n0\n0\n12\n' )
            f.write( "%d -%d %d\n" % ( 0, self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "%d -%d %d\n" % ( self.numLanes[ i ], self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "%d %d %d\n" % ( self.numLanes[ i ], self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "%d %d %d\n\n" % ( 0, self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "!genbox concrete curb1 6 %d .5 | xform -e -t -6 -%d 0\n" % ( self.sceneLengths[ i ], self.sceneLengths[ i ] / 2 ) )
            f.write( "!genbox concrete curb2 6 %d .5 | xform -e -t %d -%d 0\n" % ( self.sceneLengths[ i ], self.numLanes[ i ], self.sceneLengths[ i ] / 2 ) )
            f.write( "!xform -e -t 23.6667 -%d .001 -a 2 -t .6667 0 0 solidyellow.rad\n" % ( self.sceneLengths[ i ] / 2 ) )
            f.write( "!xform -e -t 12 -%d .001 -a 120 -t 0 20 0 -a 2 -t 24 0 0 dashed_white.rad\n\n" % ( self.sceneLengths[ i ] ) )
    
            f.write( 'grass polygon lawn1\n0\n0\n12\n' )
            f.write( "-%d -%d .5\n" % ( 6, self.sceneLengths[ i ] / 2 ) )
            f.write( "-%d %d .5\n" % ( 6, self.sceneLengths[ i ] / 2 ) )
            f.write( "-%d %d .5\n" % ( 506, self.sceneLengths[ i ] / 2 ) )
            f.write( "-%d -%d .5\n\n\n" % ( 506, self.sceneLengths[ i ] / 2 ) )
    
            f.write( 'grass polygon lawn2\n0\n0\n12\n' )
            f.write( "%d -%d .5\n" % ( 54, self.sceneLengths[ i ] / 2 ) )
            f.write( "%d %d .5\n" % ( 54, self.sceneLengths[ i ] / 2 ) )
            f.write( "%d %d .5\n" % ( 554, self.sceneLengths[ i ] / 2 ) )
            f.write( "%d -%d .5\n" % ( 554, self.sceneLengths[ i ] / 2 ) )
            self.printDashedWhiteRad( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            self.printSolidYellowRad( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            self.printPoleConfig( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            self.printLightsRad( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            self.printLuminaireRad( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            self.printNightSky( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            self.printMaterialsRad( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            
        return
        
    def printDashedWhiteRad(self, path):
        f = open( path + '/dashed_white.rad', "w" )
        f.write( "######dashed_white.rad######\n" )
        f.write( "white_paint polygon lane_dash\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "12\n" )
        f.write( "  -.1667 0 0\n")
        f.write( "   .1667 0 0\n")
        f.write( "   .1667 8 0\n")
        f.write( "  -.1667 8 0\n")
        f.close()
        return
        
    def printSolidYellowRad( self, path ):
        f = open( path + '/solid_yellow.rad', "w" )
        f.write( "######solid_yellow.rad######\n" )
        f.write( "yellow_pain polygon centre_stripe\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "12\n" )
        f.write( "  -.1667 0 0\n")
        f.write( "   .1667 0 0\n")
        f.write( "   .1667 2400 0\n")
        f.write( "  -.1667 2400 0\n")
        f.close()
        return
    
    def printPoleConfig( self, path ):
        f = open( path + 'light_pole.rad', "w" )
        f.write( "######light_pole.rad######\n" )
        f.write( "!xform -e -rz -180 -t 6 0 30 luminaire.rad\n\n" )
        f.write( "chrome cylinder pole\n" )
        f.write( "0\n")
        f.write( "0\n")
        f.write( "7\n")
        f.write( " 0 0 0\n")
        f.write( " 0 0 32\n")
        f.write( " .3333\n\n")
        f.write( "chrome cylinder mount\n" )
        f.write( "0\n")
        f.write( "0\n")
        f.write( "7\n")
        f.write( " 0 0 30.1667\n")
        f.write( " 6 0 30.1667\n")
        f.write( " .1667\n")
        f.close( )
        return
    
    def printLightsRad( self, path ):
        f = open( path + '/lights_s.rad', "w" )
        f.write( "######lights_s.rad######\n" )
        f.write( "!xform -e -t -1 -1200 0 -a 11 -t 0 240 0 lightpole.rad\n" )
        f.write( "!xform -e -rz -180 -t 49 -1080 0 -a 10 -t 0 240 0 light_pole.rad\n" )
        f.close( )
        return
    
    def printLuminaireRad(self, path ):
        f = open( path + "/luminaire.rad", "w" )
        f.write( "######luminaire.rad######\n" )
        f.write( "void brightdata ex2_dist\n" )
        f.write( "6 corr ex2.dat source.cal src_phi2 src_theta -my\n" )
        f.write( "0\n" )
        f.write( "1 1\n" )
        f.write( "ex2_dist light ex2_light\n\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "3 2.492 2.492 2.492\n\n" )
        f.write( "ex2_light sphere ex2.s\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "4 0 0 0 0.5\n" )
        f.close( )
        return
    
    def printNightSky( self, path ):
        f = open( path + '/night_sky.rad', "w" )
        f.write( "######night_sky.rad######\n" )
        f.write( "void brightfunc skyfunc\n" )
        f.write( "2 skybright skybright.cal\n" )
        f.write( "0\n" )
        f.write( "7 -1 11.620399 8.936111 1.637813 0.033302 -0.250539 0.967533\n\n" )
        f.write( "skyfunc glow ground_glow\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "4 1e-5 8e-6 5e-6 0\n\n" )
        f.write( "ground_glow source ground\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "4 0 0 -1 180\n\n" )
        f.write( "skyfunc glow sky_glow\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "4 2e-6 2e-6 1e-5  0\n\n" )
        f.write( "sky_glow source sky\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "4 0 0 1 180\n" )
        f.close( )
        return
    
    def printMaterialsRad(self, path ):
        f = open( path + '/materials.rad', "w" )
        f.write( "######materials.rad######\n" )
        f.write( "void plastic pavement\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "5 .07 .07 .07 0 0\n\n" )
        f.write( "void plastic concrete\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "5 .14 .14 .14 0 0\n\n" )
        f.write( "void plastic yellow_paint\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "5 .7 .7 .01 0 0\n\n" )
        f.write( "void plastic white_paint\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "5 .7 .7 .7 0 0\n\n" )
        f.write( "void plastic grass\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "5 0 .1 .02 0 0\n\n" )
        f.write( "void plastic 20%_gray\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "5 .2 .2 .2 0 0\n\n" )
        f.write( "void metal chrome\n" )
        f.write( "0\n" )
        f.write( "0\n" )
        f.write( "5 .2 .2 .2 .05 .05\n" )
        f.close( )
        
        

