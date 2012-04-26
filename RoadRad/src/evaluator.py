# This Python file uses the following encoding: utf-8

import os
from xml.dom.minidom import parse
import math
import shutil
import sys
import Scene
import LDC
import Pole


#write a few documentation
class evaluator:
    
    def __init__( self, path ):
        
        #instance variables which define the relative paths
        self.rootDirPath = path
        self.radDirPrefix = "/Rads"
        self.octDirSuffix = '/Octs'
        self.radDirSuffix = '/Rads'
        self.picDirSuffix = '/Pics'
        self.ldcSuffix = '/LDCs'
        self.LMKSetMat = '/' + os.path.basename( self.rootDirPath )#'/LMKSetMat'
        print self.LMKSetMat
        #sys.exit(0)
        self.LMKSetMatFilename = '/LMKSetMat.xml'
        self.picSubDirSuffix = '/pics'
        
        self.scene = Scene.Scene
        
        #output image resolution
        self.horizontalRes = 1380
        self.verticalRes = 1030
        
        path = self.rootDirPath + self.radDirPrefix
        #print "PATH " + path
        dirList = os.listdir( path )
               
        self.focalLength = 0
        self.verticalAngle = 0
        self.horizontalAngle = 0
        self.lightType = ''
        self.viewPointDistance = 60 #according to DIN EN 13201-3     
        self.viewPointHeight = 1.5
        
        self.sensorHeight = 8.9
        self.sensorWidth = 6.64
        self.lights = []
        self.Poles = []
        
        self.parseConfig( )
        self.makeOct( )
        self.printRView( )
        self.makePic( )

        return
    
    #Scene description xml parser.
    def parseConfig( self ):
        print 'Begining to parse XML Config. for din evaluation'
        configfile = open( self.rootDirPath + "/SceneDescription.xml", 'r' )
        dom = parse( configfile )
        configfile.close( )
        
        roadDesc = dom.getElementsByTagName( 'Road' )
        if( roadDesc[0].attributes ):
            self.scene.NumLanes = int( roadDesc[0].attributes["NumLanes"].value )
            self.scene.NumPoleFields = float( roadDesc[0].attributes["NumPoleFields"].value )
            self.scene.LaneWidth = float( roadDesc[0].attributes["LaneWidth"].value )
            self.scene.SidewalkWidth = float( roadDesc[0].attributes["SidewalkWidth"].value )
        
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
                    tempPole.PolePositionX = float( pole.attributes["PositionX"].value )
                else:
                    tempPole.isSingle = False
                    tempPole.PoleSpacing = float( pole.attributes["PoleSpacing"].value )
                    isStaggered = pole.attributes["IsStaggered"].value
                    if isStaggered == "False":
                        tempPole.IsStaggered = False

                tempPole.PoleSide = pole.attributes["Side"].value
                tempPole.PoleHeight = float( pole.attributes["PoleHeight"].value )
                tempPole.PoleLDC = pole.attributes["LDC"].value
                tempPole.PoleOverhang = float(pole.attributes["PoleOverhang"].value )
                self.Poles.append(tempPole)
        
        focalLen = dom.getElementsByTagName( 'FocalLength' )
        if( focalLen[ 0 ].attributes ):
            self.focalLength = float( focalLen[ 0 ].attributes["FL"].value )
            self.calcOpeningAngle( )
        
            
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.Poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
        
        if selectedArray == -1:
            print "No Pole array defined, cannot position the object. terminating"
            sys.exit(0)             
            
        #according to DIN EN 13201
        print "pole spacing: " + str( self.Poles[0].PoleSpacing )
        self.measFieldLength = self.Poles[selectedArray].PoleSpacing * self.scene.NumPoleFields;   
        
        self.numberOfMeasurementPoints = 10
        if( self.Poles[selectedArray].PoleSpacing > 30 ):        	
        	while ( self.Poles[selectedArray].PoleSpacing / self.numberOfMeasurementPoints ) > 3:
        		self.numberOfMeasurementPoints = self.numberOfMeasurementPoints + 1
        
        print "numberOfMeasurementPoints: " + str( numberOfMeasurementPoints )
        self.measurementStepWidth = self.measFieldLength / numberOfMeasurementPoints        	
        
        print "selected Pole array: " +  str( selectedArray )
        print "PoleSpacing: " + str( self.Poles[selectedArray].PoleSpacing )
        print "measurementStepWidth: " + str( self.measurementStepWidth ) 
        print "measFieldLength: " + str( self.measFieldLength ) 
        
        print 'Sucessfully Parsed.'

    #calculate the horizontal and vertical opening angle of the camera required for the rendering
    def calcOpeningAngle( self ):
        self.verticalAngle = ( 2 * math.atan( self.sensorHeight / ( 2 * self.focalLength ) ) ) / math.pi * 180
        self.horizontalAngle = ( 2 * math.atan( self.sensorWidth / ( 2 * self.focalLength ) ) ) / math.pi * 180    
    
    
    #system call to radiance framework to generate oct files out of the various rads
    # both for the actual simulated image and the refernce pictures to determine the 
    # pixel position of the target objects
    def makeOct( self ):
        if( not os.path.isdir( self.rootDirPath + self.octDirSuffix ) ):
            os.mkdir( self.rootDirPath + self.octDirSuffix )        
        
        #make oct for scene without targets for din evaluation
        cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/night_sky.rad > {1}/scene_din.oct'.format( self.rootDirPath + self.radDirSuffix, self.rootDirPath + self.octDirSuffix )
        os.system(cmd)
    
    #Prints view point files for every lane
    #Based on the viewpoint mode, one of several viewpoints are written
    def printRView( self ):
        print 'Generating: eye.vp'
        self.rows = []
        
        #-vd 0 0.9999856 -0.0169975 is 1 degree down for the IESNA standard 
        #observer who is 273 feet (83.2104m) away from and 4.75 feet (1.4478m) above the section of 
        #pavement of interest (Rendering with Radiance, p. 400 f.)
        #viewDirection = "0 0.9999856 -0.0169975"
        
        #calc view direction according to DIN standard observer
        viewerXPosition = ( self.scene.LaneWidth * (self.scene.TargetPosition + 0.5 ) )
        viewPoint = ' {0} {1} {2} '.format( viewerXPosition, self.viewPointDistance, self.viewPointHeight )
        distanceOfMeasRows = self.scene.LaneWidth / 3
        rowXPosition = self.scene.LaneWidth
        
        
        for i in range( 3 ):
        	rowXPosition = rowXPosition * (self.scene.TargetPosition + ( i * 0.25 ) )
        	directionX = rowXPosition - viewerXPosition
        	for j in range( self.numberOfMeasurementPoints ):
        		directionY = ( i + 0.5 ) * self.measurementStepWidth
        		directionZ = 0 - self.viewPointHeight
        		viewDirection = ' {0} {1} {2} '.format( directionX, directionY, directionZ )
        		print "rview -vtv -vp " + viewPoint + " -vd " + viewDirection + " -vh " + str( self.verticalAngle ) + " -vv " + str( self.horizontalAngle ) + "\n"
        		f = open( self.workingDirPath + self.radDirPrefix + '/eye' + str( j ) + '_' + str( i ) '.vp', "w" )
                f.write( "######eye.vp######\n")
                f.write( "rview -vtv -vp " + str( self.scene.LaneWidth * (self.scene.TargetPosition + 0.5 ) ) + " " + str( ( -1 * self.scene.ViewpointDistance ) + i * 24 ) + " " + str( self.scene.ViewpointHeight ) + " -vd 0 0.9999856 -0.0169975 -vh " + str( self.verticalAngle ) + " -vv " + str( self.horizontalAngle ) + "\n" )
                f.close( )
        
    
    #System call to radiance framework for the actual rendering of the images
    def makePic(self):
            if( not os.path.isdir( self.rootDirPath + self.picDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix )
            if( not os.path.isdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix )              
            
            #make pic without target for later evaluation
            print 'out.hdr'
            cmd1 = 'rpict -vtv -vf {2}/eye0.vp -x {3} -y {4} {0}/scene_din.oct > {1}/out.hdr '.format( self.rootDirPath + self.octDirSuffix , self.rootDirPath + self.picDirSuffix +self.picSubDirSuffix, self.rootDirPath + self.radDirSuffix, self.horizontalRes, self.verticalRes )
            os.system( cmd1 )
            


