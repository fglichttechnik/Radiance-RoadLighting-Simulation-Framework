# This Python file uses the following encoding: utf-8

import os
from xml.dom.minidom import parse
import Scene
import Pole
import math
import sys
import LDC

class configGenerator:
    
    def __init__( self, path ):
        #retrieve working directory info
        self.workingDirPath = path
        print 'Working Directory: ' + self.workingDirPath
        
        self.dirIndex = []
        
        self.sceneDecriptor = "/SceneDescription.xml"
        self.radDirPrefix = "/Rads"
        self.LDCDirSuffix = "/LDCs"
        self.scene = Scene.Scene
        self.verticalAngle = 0
        self.horizontalAngle = 0
        self.focalLength = 0
        
        #millimeter
        self.sensorHeight = 8.9
        self.sensorWidth = 6.64
        
        self.Poles = []
        
        self.lights = []
        
        if( self.performFileAndDirChecks( ) ):
            self.parseConfig( )
            self.printRoadRads( )
            self.makeRadfromIES( )
            self.printDashedWhiteRad( )
            self.printSolidYellowRad( )
            self.printPoleConfig( )
            self.printLightsRad( )
            self.printLuminaireRad( )
            self.printNightSky( )
            self.printMaterialsRad( )
            self.printRView( )
            self.printTarget( )
            self.printTargets( )
            

    def parseConfig( self ):
        print 'Begining to parse XML Config.'
        configfile = open( self.workingDirPath + self.sceneDecriptor, 'r' )
        dom = parse( configfile )
        configfile.close( )
        
        roadDesc = dom.getElementsByTagName( 'Road' )
        if( roadDesc[0].attributes ):
            self.scene.NumLanes = int( roadDesc[0].attributes["NumLanes"].value )
            self.scene.Length = int( roadDesc[0].attributes["LaneLength"].value )
            self.scene.LaneWidth = int( roadDesc[0].attributes["LaneWidth"].value )
            self.scene.SidewalkWidth = int( roadDesc[0].attributes["SidewalkWidth"].value )
            self.scene.Surfacetype = roadDesc[0].attributes["Surface"].value
        
        backgroundDesc = dom.getElementsByTagName( 'Background' )
        if( backgroundDesc[0].attributes ):
            self.scene.Background = backgroundDesc[0].attributes["Context"].value
        
        viewpointDesc = dom.getElementsByTagName( 'ViewPoint' )
        if( viewpointDesc[0].attributes ):
            self.scene.ViewpointDistance = float( viewpointDesc[0].attributes["Distance"].value )
            self.scene.ViewpointHeight = float( viewpointDesc[0].attributes["Height"].value )
            self.scene.ViewpointDistanceMode = viewpointDesc[0].attributes["TargetDistanceMode"].value
        
        targetDesc = dom.getElementsByTagName( 'Target' )
        if( targetDesc[0].attributes ):
            self.scene.TargetSize = float( targetDesc[0].attributes["Size"].value )
            self.scene.TargetReflectency = float( targetDesc[0].attributes["Reflectancy"].value )
            self.scene.TargetOrientation = targetDesc[0].attributes["Position"].value
            self.scene.TargetPosition = int( targetDesc[0].attributes["OnLane"].value )
        
        LDCDesc = dom.getElementsByTagName( 'LDC' )
        for LDCEntry in LDCDesc:
            if( LDCEntry.attributes ):
                tempLDC = LDC.LDC( )
                tempLDC.LDCName = LDCEntry.attributes["Name"].value
                tempLDC.LDCLightSource = LDCEntry.attributes["LightSource"].value
                self.lights.append(tempLDC)
            
        poleDesc = dom.getElementsByTagName( 'Poles' )
        for pole in poleDesc[0].childNodes:
            if( pole.attributes ):
                tempPole = Pole.Pole( )
                if( pole.nodeName == "PoleSingle" ):
                    tempPole.isSingle = True
                    tempPole.PolePositionX = int( pole.attributes["PositionX"].value )
                else:
                    tempPole.isSingle = False
                    tempPole.PoleSpacing = int( pole.attributes["PoleSpacing"].value )
                    tempPole.IsStaggered = bool( pole.attributes["IsStaggered"].value)
                
                tempPole.PoleSide = pole.attributes["Side"].value
                tempPole.PoleHeight = int( pole.attributes["PoleHeight"].value )
                tempPole.PoleLDC = pole.attributes["LDC"].value
                self.Poles.append(tempPole)
        
        focalLen = dom.getElementsByTagName( 'FocalLength' )
        if( focalLen[ 0 ].attributes ):
            self.focalLength = float( focalLen[ 0 ].attributes["FL"].value )
            self.calcOpeningAngle( )
        
        print 'Sucessfully Parsed.'

    def calcOpeningAngle( self ):
        self.verticalAngle = ( 2 * math.atan( self.sensorHeight / ( 2 * self.focalLength ) ) ) / math.pi * 180
        self.horizontalAngle = ( 2 * math.atan( self.sensorWidth / ( 2 * self.focalLength ) ) ) / math.pi * 180
    
    
    def performFileAndDirChecks( self ):
        print 'Attempting to locate configuration in: ' + self.workingDirPath + self.sceneDecriptor
        
        if( not os.path.isdir( self.workingDirPath ) ):
            print 'Scene directory not found in the working directory, Quitting'
            return False
        
        if( not os.path.isfile( self.workingDirPath + self.sceneDecriptor ) ):
            print 'No config found, Quitting'
            return False
        
        print 'Found: ' + self.sceneDecriptor
        
        if( not os.path.isdir( self.workingDirPath + self.radDirPrefix ) ):
            os.mkdir( self.workingDirPath + self.radDirPrefix )
            print 'Made directory Rads to output the Rad configs.'
        
        return True
    
    def printRoadRads( self ):
        print 'Generating: road.rad'
        f = open( self.workingDirPath + self.radDirPrefix + '/road.rad', "w" )
    
        f.write( '######road.rad######\npavement polygon pave_surf\n0\n0\n12\n' )
        f.write( "%d -%d %d\n" % ( 0, self.scene.Length / 2, 0 ) )
        f.write( "%d -%d %d\n" % ( self.scene.NumLanes * self.scene.LaneWidth, self.scene.Length / 2, 0 ) )
        f.write( "%d %d %d\n" % ( self.scene.NumLanes * self.scene.LaneWidth, self.scene.Length / 2, 0 ) )
        f.write( "%d %d %d\n\n" % ( 0, self.scene.Length / 2, 0 ) )
        f.write( "!genbox concrete curb1 %d %d .5 | xform -e -t -%d -%d 0\n" % ( self.scene.SidewalkWidth, self.scene.Length, self.scene.SidewalkWidth, self.scene.Length / 2 ) )
        f.write( "!genbox concrete curb2 %d %d .5 | xform -e -t %d -%d 0\n" % ( self.scene.SidewalkWidth, self.scene.Length, self.scene.NumLanes * self.scene.LaneWidth, self.scene.Length / 2 ) )
        #f.write( "!xform -e -t 23.6667 -%d .001 -a 2 -t .6667 0 0 %sdashed_white.rad\n" % ( self.sceneLengths[ i ] / 2, self.rootDirPath + self.sceneDirPrefix + str( i ) + '/' ) )
        f.write( "!xform -e -t %d -%d .001 -a 2000 -t 0 20 0 -a 1 -t %d 0 0 %s/dashed_white.rad\n\n" % ( self.scene.LaneWidth, self.scene.Length, self.scene.LaneWidth, self.workingDirPath + self.radDirPrefix ) )

        f.write( 'grass polygon lawn1\n0\n0\n12\n' )
        f.write( "-%d -%d .5\n" % ( self.scene.SidewalkWidth, self.scene.Length / 2 ) )
        f.write( "-%d %d .5\n" % ( self.scene.SidewalkWidth, self.scene.Length / 2 ) )
        f.write( "-%d %d .5\n" % ( 55506, self.scene.Length / 2 ) )
        f.write( "-%d -%d .5\n\n\n" % ( 55506, self.scene.Length / 2 ) )
    
        f.write( 'grass polygon lawn2\n0\n0\n12\n' )
        f.write( "%d -%d .5\n" % ( self.scene.NumLanes * self.scene.LaneWidth + self.scene.SidewalkWidth, self.scene.Length / 2 ) )
        f.write( "%d %d .5\n" % ( self.scene.NumLanes * self.scene.LaneWidth + self.scene.SidewalkWidth, self.scene.Length / 2 ) )
        f.write( "%d %d .5\n" % ( 1140, self.scene.Length / 2 ) )
        f.write( "%d -%d .5\n" % ( 1140, self.scene.Length / 2 ) )
        
        if self.scene.Background == 'City':
            f.write( "!genbox concrete building_left 50 100 100 | xform -e -t -%d 0 0 | xform -a 20 -t 0 20 0\n" % ( self.scene.NumLanes * self.scene.LaneWidth + self.scene.SidewalkWidth + 2 ) )
            f.write( "!genbox concrete building_right 50 100 100 | xform -e -t %d 0 0 | xform -a 20 -t 0 20 0\n" % ( self.scene.NumLanes * self.scene.LaneWidth + self.scene.SidewalkWidth + 2 ) )
        
        f.close()
        
    def makeRadfromIES( self ):
        if( not os.path.isdir( self.workingDirPath + self.LDCDirSuffix ) ):
            print "LDCs directory not found. Terminating."
            sys.exit(0)
        
        for entry in self.lights:
            if( not os.path.isfile( self.workingDirPath + self.LDCDirSuffix + '/' + entry.LDCName + '.ies' ) ):
                print entry.LDCName + " LDC not found in the designated LDCs directory. Terminating."
                sys.exit(0)
            
            iesPath = self.workingDirPath + self.LDCDirSuffix + '/' + entry.LDCName + '.ies'
            cmd = 'ies2rad -t ' + entry.LDCLightSource + ' -l ' + self.workingDirPath + self.LDCDirSuffix + ' ' + iesPath
            #cmd = 'ies2Rad -t ' + entry.LDCLightSource + ' ' + iesPath
            os.system( cmd )
        
    def printDashedWhiteRad(self):
            print 'Generating: dashed_white.rad'
            f = open( self.workingDirPath + self.radDirPrefix + '/dashed_white.rad', "w" )
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
        
    def printSolidYellowRad( self ):
            print 'Generating: solid_yellow.rad'
            f = open( self.workingDirPath + self.radDirPrefix + '/solid_yellow.rad', "w" )
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
    
    def printPoleConfig( self ):
            print 'Generating: Light Pole Rad files'
            
            for entry in self.Poles:
                f = open( self.workingDirPath + self.radDirPrefix + '/' + entry.PoleLDC +'_light_pole.rad', "w" )
                f.write( "######light_pole.rad######\n" )
                f.write( "!xform -e -rz -180 -t 6 0 " + str( entry.PoleHeight ) + " " + self.workingDirPath + self.radDirPrefix + "/" + entry.PoleLDC + ".rad\n\n" )
                f.write( "chrome cylinder pole\n" )
                f.write( "0\n")
                f.write( "0\n")
                f.write( "7\n")
                f.write( " 0 0 0\n")
                f.write( " 0 0 " + str( entry.PoleHeight ) + "\n")
                f.write( " .3333\n\n")
                f.write( "chrome cylinder mount\n" )
                f.write( "0\n")
                f.write( "0\n")
                f.write( "7\n")
                f.write( " 0 0 " + str( entry.PoleHeight ) + "\n")
                f.write( " 6 0 " + str( entry.PoleHeight ) + "\n")
                f.write( " .1667\n")
                f.close( )
    
    def printLightsRad( self ):
            print 'Generating: light_s.rad'
            firstArrayHandled = False
            f = open( self.workingDirPath + self.radDirPrefix + '/lights_s.rad', "w" )
            f.write( "######lights_s.rad######\n" )
            for poleArray in self.Poles:
                if poleArray.isSingle == True:
                    if poleArray.PoleSide == "Left":
                        f.write( "!xform  -t -1 " + str( poleArray.PolePositionX ) + " 0 " + self.workingDirPath + self.radDirPrefix + "/" + poleArray.PoleLDC + "_light_pole.rad\n" )
                    else:
                        f.write( "!xform -rz -180 -t "+ str( self.scene.NumLanes * self.scene.LaneWidth + 1 )+" " + str( poleArray.PolePositionX ) + " 0 " + self.workingDirPath + self.radDirPrefix + "/" + poleArray.PoleLDC + "_light_pole.rad\n" )
                elif poleArray.PoleSide == "Left":
                    print "making left poles"
                    if firstArrayHandled == False or poleArray.IsStaggered == False:
                        f.write( "!xform  -t -1 -"+ str(poleArray.PoleSpacing) +" 0 -a 4 -t 0 "+ str(poleArray.PoleSpacing) +" 0 " + self.workingDirPath + self.radDirPrefix + "/" + poleArray.PoleLDC + "_light_pole.rad\n" )
            #f.write( "!xform -e -t -1 -"+ str(self.Poles[0].PoleSpacing) +" 0 -a 4 -t 0 "+ str(self.Poles[0].PoleSpacing) +" 0 " + self.workingDirPath + self.radDirPrefix + "/light_pole.rad\n" )
                        firstArrayHandled = True
                    else:
                        f.write( "!xform  -t -1 -" + str( 0.5 * poleArray.PoleSpacing) +" 0 -a 4 -t 0 "+ str(poleArray.PoleSpacing) +" 0 " + self.workingDirPath + self.radDirPrefix + "/" + poleArray.PoleLDC + "_light_pole.rad\n" )
                else:
                    print "making right poles"
                    if firstArrayHandled == False or poleArray.IsStaggered == False:
                        f.write( "!xform  -rz -180 -t " + str( self.scene.NumLanes * self.scene.LaneWidth + 1 ) + " -"+ str(poleArray.PoleSpacing) +" 0 -a 4 -t 0 "+ str(poleArray.PoleSpacing) +" 0 " + self.workingDirPath + self.radDirPrefix + "/" + poleArray.PoleLDC + "_light_pole.rad\n" )
                        firstArrayHandled = True
                    else:
                        f.write( "!xform  -rz -180 -t " + str( self.scene.NumLanes * self.scene.LaneWidth + 1 ) + " -"+ str( 0.5 * poleArray.PoleSpacing) +" 0 -a 4 -t 0 "+ str(poleArray.PoleSpacing) +" 0 " + self.workingDirPath + self.radDirPrefix + "/" + poleArray.PoleLDC + "_light_pole.rad\n" )
            #f.write( "!xform -e -t -1 -120 0 -a 4 -t 0 240 0 " + self.workingDirPath + self.radDirPrefix + "/light_pole.rad\n" )
            #f.write( "!xform -e -rz -180 -t " + str( self.scene.NumLanes * self.scene.LaneWidth + 1 ) + " -240 0 -a 10 -t 0 240 0 " + self.workingDirPath + self.radDirPrefix + "/light_pole.rad\n" )
            f.close( )
    
    def printLuminaireRad( self ):
            print 'Generating: LDC Rad files'
            
            for entry in self.lights:
                f = open( self.workingDirPath + self.radDirPrefix + '/' + entry.LDCName + '.rad', "w" )
                f.write( "######luminaire.rad######\n" )
                f.write( "void brightdata ex2_dist\n" )
                f.write( "6 corr " + self.workingDirPath + "/LDCs/" + entry.LDCName + ".dat" + " source.cal src_phi2 src_theta -my\n" )
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
    
    def printNightSky( self ):
            print 'Generating: night_sky.rad'
            f = open( self.workingDirPath + self.radDirPrefix + '/night_sky.rad', "w" )
            f.write( "######night_sky.rad######\n" )
            f.write( "void brightfunc skyfunc\n" )
            f.write( "2 skybr skybright.cal\n" )
            f.write( "0\n" )
            f.write( "7 -1 11.620399 8.936111 1.637813 0.033302 -0.250539 0.967533\n\n" )
            f.write( "skyfunc glow ground_glow\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 1e-5 8e-6 5e-6 0\n\n" )
            #here for ref image
            #f.write( "4 1 1 1 0\n\n" )
            f.write( "ground_glow source ground\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 0 0 -1 180\n\n" )
            f.write( "skyfunc glow sky_glow\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 2e-6 2e-6 1e-5  0\n\n" )
            #here for ref image
            #f.write( "4 0 0 0  0\n\n" )
            f.write( "sky_glow source sky\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 0 0 1 180\n" )
            f.close( )
    
    def printMaterialsRad( self ):
            print 'Generating: materials.rad'
            f = open( self.workingDirPath + self.radDirPrefix + '/materials.rad', "w" )
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
            f.write( "5 .2 .2 .2 .05 .05\n\n" )
            f.write( "void glow self_box\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 1 1 1 0\n\n" )
            f.close( )
    
    def printRView( self ):
        print 'Generating: eye.vp'
        
        if self.scene.ViewpointDistanceMode == 'fixedViewPoint':
            f = open( self.workingDirPath + self.radDirPrefix + '/eye.vp', "w" )
            f.write( "######eye.vp######\n")
            f.write( "rview -vtv -vp " + str( self.scene.LaneWidth * (self.scene.TargetPosition + 0.5 ) ) +" -" + str( self.scene.ViewpointDistance ) + " " + str( self.scene.ViewpointHeight ) + " -vd 0 0.9999856 -0.0169975 -vh " + str( self.verticalAngle ) + " -vv " + str( self.horizontalAngle ) + "\n" )
            f.close( )
        else:
            for i in range( 14 ):
                f = open( self.workingDirPath + self.radDirPrefix + '/eye' + str( i ) + '.vp', "w" )
                f.write( "######eye.vp######\n")
                f.write( "rview -vtv -vp " + str( self.scene.LaneWidth * (self.scene.TargetPosition + 0.5 ) ) + " " + str( ( -1 * self.scene.ViewpointDistance ) + i * 24 ) + " " + str( self.scene.ViewpointHeight ) + " -vd 0 0.9999856 -0.0169975 -vh " + str( self.verticalAngle ) + " -vv " + str( self.horizontalAngle ) + "\n" )
                f.close( )
    
    def printTarget( self ):
            print 'Generating: target.rad'
            f = open( self.workingDirPath + self.radDirPrefix + '/target.rad', "w" )
            f.write( "######target.rad######\n")
            f.write( "!genbox 20%_gray stv_target 2 2 2\n" )
            f.close( )
            
            f = open( self.workingDirPath + self.radDirPrefix + '/self_target.rad', "w" )
            f.write( "######target.rad######\n")
            f.write( '!genbox self_box stv_target {0} {0} 2\n'.format( self.scene.TargetSize ) )
            f.close( )
    
    def printTargets( self ):
            dist = 0
            for i in range( 14 ):
                print 'Generating: target_' + str( i ) + '.rad'
                f = open( self.workingDirPath + self.radDirPrefix + '/target_' + str( i ) + '.rad', "w" )
                f.write( "######target_0.rad######\n")
                f.write( "!xform -e -t " + str( self.scene.LaneWidth * (self.scene.TargetPosition + 0.5 ) ) + " " + str( dist ) + " 0 " + self.workingDirPath + self.radDirPrefix + "/target.rad\n" )
                f.close( )
                dist = dist + 24
            
            dist = 0
            for i in range( 14 ):
                print 'Generating: self_target_' + str( i ) + '.rad'
                f = open( self.workingDirPath + self.radDirPrefix + '/self_target_' + str( i ) + '.rad', "w" )
                f.write( "######target_0.rad######\n")
                f.write( "!xform -e -t " + str( self.scene.LaneWidth * (self.scene.TargetPosition + 0.5 ) ) + " " + str( dist ) + " 0 " + self.workingDirPath + self.radDirPrefix + "/self_target.rad\n" )
                f.close( )
                dist = dist + 24
        
        

