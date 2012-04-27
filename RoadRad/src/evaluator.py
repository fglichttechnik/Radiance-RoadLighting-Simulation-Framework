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
        self.picSubDirSuffix = '/pics'
        
        self.scene = Scene.Scene
        
        #output image resolution
        self.horizontalRes = 1380
        self.verticalRes = 1030
               
        self.focalLength = 0
        self.verticalAngle = 0
        self.horizontalAngle = 0
        self.viewPointDistance = 60 #according to DIN EN 13201-3     
        self.viewPointHeight = 1.5
        
        self.sensorHeight = 8.9
        self.sensorWidth = 6.64
        self.lights = []
        self.Poles = []
        
        self.parseConfig( )
        self.makeOct( )
        self.calcLuminances( )
        self.calcIlluminances( )
        #self.makePic( )

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
		
    	print 'Generating: luminance values according to DIN EN 13201-3'
		
    	#according to DIN EN 13201
        print "	pole spacing: " + str( self.Poles[0].PoleSpacing )
        self.measFieldLength = self.Poles[0].PoleSpacing * self.scene.NumPoleFields   
        
        self.numberOfMeasurementPoints = 10
        if( self.Poles[0].PoleSpacing > 30 ):        	
        	while ( self.Poles[0].PoleSpacing / self.numberOfMeasurementPoints ) > 3:
        		self.numberOfMeasurementPoints = self.numberOfMeasurementPoints + 1
        
        print "	number of measurement points: " + str( self.numberOfMeasurementPoints )
        self.measurementStepWidth = self.measFieldLength / self.numberOfMeasurementPoints        
        print "	measurement step width: " + str( self.measurementStepWidth ) 
        print "	measurment field length: " + str( self.measFieldLength ) 
    
    	directionZ = self.viewPointHeight   
        f = open( self.workingDirPath + self.radDirPrefix + '/luminanceCoordinates.pos', "w" )
        
    	for laneNumber in range( self.scene.NumLanes ):    		        
			#
        	print "	lane: " + str( laneNumber + 1 )
        	#
        	#calc view direction according to DIN standard observer
        	viewerXPosition = ( self.scene.LaneWidth * (laneNumber + 0.5 ) )
        	print '		viewer X position: ' + str( viewerXPosition )
        	viewPoint = ' {0} {1} {2}'.format( viewerXPosition, self.viewPointDistance, self.viewPointHeight )
        	distanceOfMeasRows = self.scene.LaneWidth / 3
        	#
        	for rowNumber in range( 3 ):        		
        		rowXPosition = self.scene.LaneWidth * (laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
        		print '		row x position: ' + str( rowXPosition )
        		directionX = viewerXPosition -rowXPosition
        		#
        		for measPointNumber in range( self.numberOfMeasurementPoints ):
        			directionY = self.viewPointDistance - ( ( measPointNumber + 0.5 ) * self.measurementStepWidth )
        			viewDirection = ' {0} {1} {2}'.format( directionX, directionY, directionZ )
        			f.write( str( viewPoint ) + str( viewDirection ) + '\n')
                	
                	
        f.close( )
        
        cmd = "rtrace -h -oo -od -ov /Users/sandy/Desktop/Development/RoadRad/RoadRad/scenes/Treskowstr_LED_RP8_4/Octs/scene_din.oct < " + self.workingDirPath + self.radDirPrefix + "/luminanceCoordinates.pos  | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.workingDirPath + self.radDirPrefix + "/rawLuminances.txt"
        os.system( cmd )
        cmd = "rlam " + self.workingDirPath + self.radDirPrefix + "/luminanceCoordinates.pos " + self.workingDirPath + self.radDirPrefix + "/rawLuminances.txt > " + self.workingDirPath + self.radDirPrefix + "/luminances.txt"
        os.system( cmd )
        print "Luminance values successfully calculated"
        
    #Prints view point files for every lane
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcIlluminances( self ):    
		
    	print 'Generating: illuminance values according to DIN EN 13201-3'
		
    	#according to DIN EN 13201
        print "	pole spacing: " + str( self.Poles[0].PoleSpacing )
        self.measFieldLength = self.Poles[0].PoleSpacing * self.scene.NumPoleFields   
        
        self.numberOfMeasurementPoints = 10
        if( self.Poles[0].PoleSpacing > 30 ):        	
        	while ( self.Poles[0].PoleSpacing / self.numberOfMeasurementPoints ) > 3:
        		self.numberOfMeasurementPoints = self.numberOfMeasurementPoints + 1
        
        print "	number of measurement points: " + str( self.numberOfMeasurementPoints )
        self.measurementStepWidth = self.measFieldLength / self.numberOfMeasurementPoints        
        print "	measurement step width: " + str( self.measurementStepWidth ) 
        print "	measurment field length: " + str( self.measFieldLength ) 
    
    	viewDirection = '0 0 -1'
    	positionZ = '0.02'
    	
    	self.numberOfMeasurementRows = 3
    	while ( self.scene.LaneWidth / self.numberOfMeasurementRows ) > 1.5:
    		self.numberOfMeasurementRows = self.numberOfMeasurementRows + 1
    		
    	print "	number of measurement rows per lane: " + str( self.numberOfMeasurementRows )
    	
    	f = open( self.workingDirPath + self.radDirPrefix + '/illuminanceCoordinates.pos', "w" )
    	
    	for laneNumber in range( self.scene.NumLanes ):
    		#
    		print "	lane: " + str( laneNumber +1 )
    		#
    		for rowNumber in range( self.numberOfMeasurementRows ):
    			positionX = self.scene.LaneWidth * (laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
    			print "		position X: " + str( positionX )
    			#
    			for measPointNumber in range( self.numberOfMeasurementPoints ):
    				positionY = ( ( measPointNumber + 0.5 ) * self.measurementStepWidth )
    				viewPoint = '{} {} {} '.format( positionX, positionY, positionZ )
    				print '			' + str(viewPoint ) + str( viewDirection )
    				f.write( str(viewPoint ) + str( viewDirection ) + '\n' )
    	             	
                	
        f.close( )
        
        cmd1 = "rtrace -h -I /Users/sandy/Desktop/Development/RoadRad/RoadRad/scenes/Treskowstr_LED_RP8_4/Octs/scene_din.oct < " + self.workingDirPath + self.radDirPrefix + "/illuminanceCoordinates.pos  | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.workingDirPath + self.radDirPrefix + "/rawIlluminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam " + self.workingDirPath + self.radDirPrefix + "/illuminanceCoordinates.pos " + self.workingDirPath + self.radDirPrefix + "/rawIlluminances.txt > " + self.workingDirPath + self.radDirPrefix + "/illuminances.txt"
        os.system( cmd2 )
        print "Illuminance values successfully calculated"
    
    
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
            


