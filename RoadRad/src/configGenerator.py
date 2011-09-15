# This Python file uses the following encoding: utf-8

import os
import sys
from xml.dom.minidom import parse

class configGenerator:
    
    def __init__( self, workingDir ):
        #retrieve working directory info
        self.rootDirPath = workingDir
        print 'Working Directory: ' + self.rootDirPath
        
        self.rootDirPath = workingDir
        self.dirIndex = []
        
        #dirList = os.listdir( self.rootDirPath )
        #for entry in dirList:
        #    if( os.path.isdir( entry ) ):
        #        if( "scene" in entry ):
        #            self.dirIndex.append( self.rootDirPath + '/' + entry )
        #            print "Found: " + entry
        
        self.xmlConfigsPrefix = '/configs/'
        
        self.sceneDirPrefix = '/scenes/scene'
        
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
        
    
    def parseRoads( self ):
        if( not self.performFileAndDirChecks( self.roadFileName ) ):
            return False
        
        print 'Attempting to parse road scenes'
        if( not self.parseRoadScenes( self.rootDirPath + self.xmlConfigsPrefix + self.roadFileName ) ):
            print 'Error parsing road.xml, check syntax'
            return False
        
        self.printRoadRads( )
        return True
        
    def parsePoles( self ):
        if( not self.performFileAndDirChecks( self.poleFileName ) ):
            return False
        
        print 'Attempting to parse pole configs'
        if( not self.parsePoleConfigs( self.rootDirPath + self.xmlConfigsPrefix + self.poleFileName ) ):
            print 'Error parsing road.xml, check syntax'
            return False
        
        print self.printPoleConfig( )
        return False
    
    def performFileAndDirChecks( self, prefix ):
        print 'Attempting to locate XML config files in: ' + self.rootDirPath + self.xmlConfigsPrefix
        
        if( not os.path.isdir( self.rootDirPath + self.xmlConfigsPrefix ) ):
            print 'Config directory not found in the working directory, Quitting'
            return False
        
        if( not os.path.isfile( self.rootDirPath + self.xmlConfigsPrefix + prefix ) ):
            print prefix + ': File not found, Quitting'
            return False
        
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
    
    def printRoadRads( self ):
        
        for i in range( 0, len( self.sceneLengths ) ):
            
            if( not os.path.isdir( self.rootDirPath + self.sceneDirPrefix + str( i ) ) ):
                os.mkdir( self.rootDirPath + self.sceneDirPrefix + str( i ) )
                
            self.dirIndex.append( self.rootDirPath + self.sceneDirPrefix + str( i ) )
            
            f = open( self.rootDirPath + self.sceneDirPrefix + str( i ) + '/road.rad', "w" )
    
            f.write( '######road.rad######\npavement polygon pave_surf\n0\n0\n12\n' )
            f.write( "%d -%d %d\n" % ( 0, self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "%d -%d %d\n" % ( self.pavementWidths[ i ], self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "%d %d %d\n" % ( self.pavementWidths[ i ], self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "%d %d %d\n\n" % ( 0, self.sceneLengths[ i ] / 2, 0 ) )
            f.write( "!genbox concrete curb1 6 %d .5 | xform -e -t -6 -%d 0\n" % ( self.sceneLengths[ i ], self.sceneLengths[ i ] / 2 ) )
            f.write( "!genbox concrete curb2 6 %d .5 | xform -e -t %d -%d 0\n" % ( self.sceneLengths[ i ], self.pavementWidths[ i ], self.sceneLengths[ i ] / 2 ) )
            #f.write( "!xform -e -t 23.6667 -%d .001 -a 2 -t .6667 0 0 %sdashed_white.rad\n" % ( self.sceneLengths[ i ] / 2, self.rootDirPath + self.sceneDirPrefix + str( i ) + '/' ) )
            f.write( "!xform -e -t 12 -%d .001 -a 120 -t 0 20 0 -a 1 -t 24 0 0 %sdashed_white.rad\n\n" % ( self.sceneLengths[ i ], self.rootDirPath + self.sceneDirPrefix + str( i ) + '/' ) )
    
            f.write( 'grass polygon lawn1\n0\n0\n12\n' )
            f.write( "-%d -%d .5\n" % ( 6, self.sceneLengths[ i ] / 2 ) )
            f.write( "-%d %d .5\n" % ( 6, self.sceneLengths[ i ] / 2 ) )
            f.write( "-%d %d .5\n" % ( 506, self.sceneLengths[ i ] / 2 ) )
            f.write( "-%d -%d .5\n\n\n" % ( 506, self.sceneLengths[ i ] / 2 ) )
    
            f.write( 'grass polygon lawn2\n0\n0\n12\n' )
            f.write( "%d -%d .5\n" % ( 30, self.sceneLengths[ i ] / 2 ) )
            f.write( "%d %d .5\n" % ( 30, self.sceneLengths[ i ] / 2 ) )
            f.write( "%d %d .5\n" % ( 530, self.sceneLengths[ i ] / 2 ) )
            f.write( "%d -%d .5\n" % ( 530, self.sceneLengths[ i ] / 2 ) )
        return
        
    def printDashedWhiteRad(self):
        for entry in self.dirIndex:
            f = open( entry + '/dashed_white.rad', "w" )
            f.write( "######dashed_white.rad######\n" )
            f.write( "white_paint polygon lane_dash\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "12\n" )
            f.write( "-.1667 0 0\n")
            f.write( ".1667 0 0\n")
            f.write( ".1667 8 0\n")
            f.write( "-.1667 8 0\n")
            f.close()
        return
        
    def printSolidYellowRad( self ):
        for entry in self.dirIndex:
            f = open( entry + '/solid_yellow.rad', "w" )
            f.write( "######solid_yellow.rad######\n" )
            f.write( "yellow_paint polygon centre_stripe\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "12\n" )
            f.write( "  -.1667 0 0\n")
            f.write( "   .1667 0 0\n")
            f.write( "   .1667 2400 0\n")
            f.write( "  -.1667 2400 0\n")
            f.close()
        return
    
    def printPoleConfig( self ):
        for entry in self.dirIndex:
            f = open( entry + '/light_pole.rad', "w" )
            f.write( "######light_pole.rad######\n" )
            f.write( "!xform -e -rz -180 -t 6 0 30 " + entry + "/luminaire.rad\n\n" )
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
    
    def printLightsRad( self ):
        for entry in self.dirIndex:
            f = open( entry + '/lights_s.rad', "w" )
            f.write( "######lights_s.rad######\n" )
            f.write( "!xform -e -t -1 -120 0 -a 11 -t 0 240 0 " + entry + "/light_pole.rad\n" )
            f.write( "!xform -e -rz -180 -t 25 -240 0 -a 10 -t 0 240 0 " + entry + "/light_pole.rad\n" )
            f.close( )
        return
    
    def printLuminaireRad( self ):
        for entry in self.dirIndex:
            f = open( entry + "/luminaire.rad", "w" )
            f.write( "######luminaire.rad######\n" )
            f.write( "void brightdata ex2_dist\n" )
            f.write( "6 corr " + entry + "/ex2.dat source.cal src_phi2 src_theta -my\n" )
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
    
    def printNightSky( self ):
        for entry in self.dirIndex:
            f = open( entry + '/night_sky.rad', "w" )
            f.write( "######night_sky.rad######\n" )
            f.write( "void brightfunc skyfunc\n" )
            f.write( "2 skybr skybright.cal\n" )
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
    
    def printMaterialsRad( self ):
        for entry in self.dirIndex:
            f = open( entry + '/materials.rad', "w" )
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
    
    def printRView( self ):
        for entry in self.dirIndex:
            f = open( entry + '/eye.vp', "w" )
            f.write( "######eye.vp######\n")
            f.write( "rview -vtv -vp 28 -273 4.75 -vd 0 0.9999856 -0.0169975 -vh 25 -vv 12.5\n" )
            f.close( )
        return
    
    def printTarget( self ):
        for entry in self.dirIndex:
            f = open( entry + '/target.rad', "w" )
            f.write( "######target.rad######\n")
            f.write( "!genbox 20%_gray stv_target 2 2 2\n" )
            f.close( )
        return
    
    def printTargets( self ):
        for entry in self.dirIndex:
            dist = 0
            for i in range( 14 ):
                f = open( entry + '/target_' + str( i ) + '.rad', "w" )
                f.write( "######target_0.rad######\n")
                f.write( "!xform -e -t 17 " + str( dist ) + " 0 " + entry + "/target.rad\n" )
                f.close( )
                dist = dist + 24
        return
        
        

