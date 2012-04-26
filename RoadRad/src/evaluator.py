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
        self.workingDirPath = path
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
        self.calcLuminances( )
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
                
            
        #according to DIN EN 13201
        print "pole spacing: " + str( self.Poles[0].PoleSpacing )
        self.measFieldLength = self.Poles[0].PoleSpacing * self.scene.NumPoleFields;   
        
        self.numberOfMeasurementPoints = 10
        if( self.Poles[0].PoleSpacing > 30 ):        	
        	while ( self.Poles[0].PoleSpacing / self.numberOfMeasurementPoints ) > 3:
        		self.numberOfMeasurementPoints = self.numberOfMeasurementPoints + 1
        
        print "numberOfMeasurementPoints: " + str( self.numberOfMeasurementPoints )
        self.measurementStepWidth = self.measFieldLength / self.numberOfMeasurementPoints        
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
    def calcLuminances( self ):
    	directionZ = 0 - self.viewPointHeight
    	print 'Generating: luminance view directions'
        self.rows = []   
        f = open( self.workingDirPath + self.radDirPrefix + '/luminanceCoordinates.pos', "w" )
        
    	for laneNumber in range( self.scene.NumLanes ):    		        
			#
        	print "lane index: " + str( laneNumber )
        	#
        	#calc view direction according to DIN standard observer
        	viewerXPosition = ( self.scene.LaneWidth * (laneNumber + 0.5 ) )
        	print 'viewer X position: ' + str( viewerXPosition )
        	viewPoint = ' {0} {1} {2}'.format( viewerXPosition, self.viewPointDistance, self.viewPointHeight )
        	distanceOfMeasRows = self.scene.LaneWidth / 3
        	#
        	for rowNumber in range( 3 ):        		
        		rowXPosition = self.scene.LaneWidth * (laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
        		print 'row x position: ' + str( rowXPosition )
        		directionX = rowXPosition - viewerXPosition
        		#
        		for measPointNumber in range( self.numberOfMeasurementPoints ):
        			directionY = ( ( measPointNumber + 0.5 ) * self.measurementStepWidth ) + self.viewPointDistance
        			viewDirection = ' {0} {1} {2}'.format( directionX, directionY, directionZ )
        			print ' ' + str( viewPoint ) + str( viewDirection ) + '\n'
        			f.write( str( viewPoint ) + str( viewDirection ) + '\n')
                	
                	
        f.close( )
        
        print 'Calculating: Luminances for defined rays'
        cmd = "rtrace -h -oo -od -ov /Users/sandy/Desktop/Development/RoadRad/RoadRad/scenes/Treskowstr_LED_RP8_4/Octs/scene_din.oct < " + self.workingDirPath + self.radDirPrefix + "/luminanceCoordinates.pos  | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.workingDirPath + self.radDirPrefix + "/rawLuminances.txt"
        os.system( cmd )
        cmd = "rlam " + self.workingDirPath + self.radDirPrefix + "/luminanceCoordinates.pos " + self.workingDirPath + self.radDirPrefix + "/rawLuminances.txt > " + self.workingDirPath + self.radDirPrefix + "/luminances.txt"
        os.system( cmd )
        
    
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
            


