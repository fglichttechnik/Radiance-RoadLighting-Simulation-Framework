# This Python file uses the following encoding: utf-8

import os
from xml.dom.minidom import parse
import math
import shutil
import sys
import csv
import struct
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
        self.evalDirSuffix = '/Evaluation'
        
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
        
        self.meanLuminance = 0.0
        self.uniformityOfLuminance = 0.0
        self.lengthwiseUniformityOfLuminance = 0.0
        self.meanIlluminance = 0.0
        self.minIlluminance = 0.0
        self.uniformityOfIlluminance = 0.0
        
        self.parseConfig( )
        self.makeOct( )
        self.calcLuminances( )
        self.calcIlluminances( )
        #self.makePic( )
        #self.makeFalsecolor( )
        self.evalLuminance( )
        self.evalIlluminance( )

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
    
    	directionZ = 0 - self.viewPointHeight   
    	viewerYPosition = - self.viewPointDistance
    	viewerZPosition = self.viewPointHeight
        f = open( self.workingDirPath + self.radDirPrefix + '/luminanceCoordinates.pos', "w" )
        l = open( self.workingDirPath + self.radDirPrefix + '/luminanceLanes.pos', "w" )
        
    	for laneNumber in range( self.scene.NumLanes ):    		        
			#
        	print "	lane: " + str( laneNumber + 1 )
        	#
        	#calc view direction according to DIN standard observer
        	viewerXPosition = ( self.scene.LaneWidth * (laneNumber + 0.5 ) )
        	print '		viewer X position: ' + str( viewerXPosition )
        	viewPoint = '{0} {1} {2}'.format( viewerXPosition, viewerYPosition, viewerZPosition )
        	distanceOfMeasRows = self.scene.LaneWidth / 3
        	#
        	for rowNumber in range( 3 ):        		
        		rowXPosition = self.scene.LaneWidth * (laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
        		print '		row x position: ' + str( rowXPosition )
        		directionX = rowXPosition - viewerXPosition
        		#
        		for measPointNumber in range( self.numberOfMeasurementPoints ):
        			directionY = ( ( measPointNumber + 0.5 ) * self.measurementStepWidth ) - viewerYPosition
        			viewDirection = ' {0} {1} {2}'.format( directionX, directionY, directionZ )
        			f.write( str( viewPoint ) + str( viewDirection ) + ' \n')
        			l.write( str( laneNumber) + ' ' + str( rowNumber ) + ' \n' )
                	
                	
        f.close( )
        l.close( )
        
        cmd1 = "rtrace -h -oo -od -ov /Users/sandy/Desktop/Development/RoadRad/RoadRad/scenes/Treskowstr_LED_RP8_4/Octs/scene_din.oct < " + self.workingDirPath + self.radDirPrefix + "/luminanceCoordinates.pos  | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.workingDirPath + self.radDirPrefix + "/rawLuminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t {0}/luminanceLanes.pos {0}/luminanceCoordinates.pos {0}/rawLuminances.txt >  {0}/luminances.txt".format( self.workingDirPath + self.radDirPrefix )
        os.system( cmd2 )
        print "Done."
        
    #Prints view point files for every lane
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcIlluminances( self ):    
		
    	print 'Generating: illuminance values at measurement points according to DIN EN 13201-3'
		
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
    
    	viewDirection = '0 0 1'
    	positionZ = '0.02'
    	
    	self.numberOfMeasurementRows = 3
    	while ( self.scene.LaneWidth / self.numberOfMeasurementRows ) > 1.5:
    		self.numberOfMeasurementRows = self.numberOfMeasurementRows + 1
    		
    	print "	number of measurement rows per lane: " + str( self.numberOfMeasurementRows )
    	
    	f = open( self.workingDirPath + self.radDirPrefix + '/illuminanceCoordinates.pos', "w" )
    	l = open( self.workingDirPath + self.radDirPrefix + '/illuminanceLanes.pos', "w" )
    	
    	for laneNumber in range( self.scene.NumLanes ):
    		#
    		for rowNumber in range( self.numberOfMeasurementRows ):
    			positionX = self.scene.LaneWidth * (laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
    			#
    			for measPointNumber in range( self.numberOfMeasurementPoints ):
    				positionY = ( ( measPointNumber + 0.5 ) * self.measurementStepWidth )
    				viewPoint = '{} {} {} '.format( positionX, positionY, positionZ )
    				f.write( str( viewPoint ) + str( viewDirection ) + ' \n' )
    				l.write( str( laneNumber) + ' ' + str( rowNumber ) + ' \n' )
    	             	
                	
        f.close( )
        l.close( )
        
        cmd1 = "rtrace -h -I+ -w -ab 1 " + self.rootDirPath + self.octDirSuffix + "/scene_din.oct < " + self.workingDirPath + self.radDirPrefix + "/illuminanceCoordinates.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.workingDirPath + self.radDirPrefix + "/rawIlluminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t  {0}/illuminanceLanes.pos {0}/illuminanceCoordinates.pos {0}/rawIlluminances.txt > {0}/illuminances.txt".format( self.workingDirPath + self.radDirPrefix )
        os.system( cmd2 )
        print "Done."
    
    
    def makePic(self):
            if( not os.path.isdir( self.rootDirPath + self.picDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix )
            if( not os.path.isdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix )              
            
            #make pic without target for later evaluation
            print 'out_radiance.hdr'
            cmd1 = 'rpict -vtv -vf {2}/eye0.vp -x {3} -y {4} {0}/scene_din.oct > {1}/out_radiance.hdr '.format( self.rootDirPath + self.octDirSuffix , self.rootDirPath + self.picDirSuffix +self.picSubDirSuffix, self.rootDirPath + self.radDirSuffix, self.horizontalRes, self.verticalRes )
            os.system( cmd1 )
            print 'out_irradiance.hdr'
            cmd2 = 'rpict -i -vtv -vf {2}/eye0.vp -x {3} -y {4} {0}/scene_din.oct > {1}/out_irradiance.hdr '.format( self.rootDirPath + self.octDirSuffix , self.rootDirPath + self.picDirSuffix +self.picSubDirSuffix, self.rootDirPath + self.radDirSuffix, self.horizontalRes, self.verticalRes )
            os.system( cmd2 )
            
    def makeFalsecolor( self ):
    		print 'falsecolor_luminance.hdr'
    		cmd0 = 'falsecolor -i {0}/out_radiance.hdr -log 5 -l cd/m^2 > {0}/falsecolor_luminance.hdr'.format( self.rootDirPath + self.picDirSuffix +self.picSubDirSuffix )
    		os.system( cmd0 )
    		print 'falsecolor_illuminance.hdr'
    		cmd1 = 'falsecolor -i {0}/out_irradiance.hdr -log 5 -l lx > {0}/falsecolor_illuminance.hdr'.format( self.rootDirPath + self.picDirSuffix +self.picSubDirSuffix )
    		os.system( cmd1 )
    		    
    
    def evalLuminance( self ):
    	print 'Evaluate luminances...'    	    	
    	
    	L_min_ = []
    	L_m_ = []
    	U_0_ = []
    	
    	L_l_min_ = []
    	L_l_m_ = []
    	U_l_ = []
    	
    	for lane in range( self.scene.NumLanes ):
    		print '	lane: ' + str( lane )
    		lumFile = open( self.workingDirPath + self.radDirPrefix + '/luminances.txt', 'r')
    		lumReader = csv.reader( lumFile, delimiter = ' ' )
    		
    		L = []
    		L_l = []
    		
    		L_m_lane = 0
    		L_l_m_lane = 0
    		
    		L_m_values = 0
    		L_l_values = 0
    		
    		for row in lumReader:
    			if( float( row[0] ) == float( lane ) ):
    				L_row = float( row[8] )
    				L_m_lane += float( row[8] )
    				L_m_values += 1
    				L.append( L_row)
    				#
    				if( float( row[1] ) == 1 ):
    						L_l_row = float( row[8] )
    						L_l_values += 1
    						L_l_m_lane += float( row[8] )
    						L_l.append( L_l_row )
    		#
    		L_m_.append( L_m_lane / L_m_values )
    		L_m_lane = L_m_lane / L_m_values
    		L_min_lane = min( L )
    		L_min_.append( L_min_lane )
    		U_0_.append( L_min_lane / L_m_lane )
    		#
    		print '		L_m of lane ' + str( lane ) + ':			' + str( L_m_lane )
    		print '		L_min of lane ' + str( lane ) + ':		' + str( L_min_[lane] )
    		print '		U_0 of lane ' + str( lane ) + ':			' + str( U_0_[lane] )
    		#
    		L_l_m_.append( L_l_m_lane / L_l_values )
    		L_l_m_lane = L_l_m_lane / L_l_values
    		L_l_min_lane = min( L_l )
    		L_l_min_.append( L_l_min_lane )
    		U_l_.append( L_l_min_lane / L_l_m_lane )
    		#
    		print '		L_m lengthwise of lane ' + str( lane ) + ':	' + str( L_l_m_lane )
    		print '		L_min lengthwise of lane ' + str( lane ) + ':	' + str( L_l_min_[lane] )
    		print '		U_l of lane ' + str( lane ) + ':			' + str( U_l_[lane] )
    		#
    		lumFile.close( )
        		
		L_m = min( L_m_ )
		L_min = min( L_min_ )
        U_0 = min( U_0_ )
        U_l = min( U_l_ )
        
        print '	L_m = ' + str( L_m )
        print '	U_0 = ' + str( U_0 )
        print '	U_l = ' + str( U_l )
        
        self.meanLuminance = L_m
        self.uniformityOfLuminance = U_0
        self.lengthwiseUniformityOfLuminance = U_l
        
        print "Done."			
        
    def evalIlluminance( self ):
    	print 'Evaluate illuminances...'    	    	
    	
    	E_min_ = []
    	E_m_ = []
    	g_1_ = []
    	    	
    	for lane in range( self.scene.NumLanes ):
    		print '	lane: ' + str( lane )
    		lumFile = open( self.workingDirPath + self.radDirPrefix + '/illuminances.txt', 'r')
    		lumReader = csv.reader( lumFile, delimiter = ' ' )
    		
    		E = []    		
    		E_m_lane = 0    		
    		E_m_values = 0
    		
    		for row in lumReader:
    			if( float( row[0] ) == float( lane ) ):
    				E_row = float( row[8] )
    				E_m_lane += float( row[8] )
    				E_m_values += 1
    				E.append( E_row)
    		#
    		E_m_.append( E_m_lane / E_m_values )
    		E_m_lane = E_m_lane / E_m_values
    		E_min_lane = min( E )
    		E_min_.append( E_min_lane )
    		g_1_.append( E_min_lane / E_m_lane )
    		#
    		print '		E_m of lane ' + str( lane ) + ':			' + str( E_m_lane )
    		print '		E_min of lane ' + str( lane ) + ':		' + str( E_min_[lane] )
    		print '		g_1 of lane ' + str( lane ) + ':			' + str( g_1_[lane] )
    		#
    		lumFile.close( )
        		
		E_m = min( E_m_ )
		E_min = min( E_min_ )
        g_1 = min( g_1_ )
        
        print '	E_m = ' + str( E_m )
        print '	E_min = ' + str( E_min)
        print '	g_1 = ' + str( g_1 )
        
        self.meanIlluminance = E_m
        self.minIlluminance = E_min        
        self.uniformityOfIlluminance = g_1
        
        print "Done."	
    
    
    def makeXML( self ):
    		print 'Generating XML: file..'
    		if( not os.path.isdir( self.rootDirPath + self.evalDirSuffix ) ):
    			os.mkdir( self.rootDirPath + self.evalDirSuffix )
    		
    		

			
            
            
    		
    		
    		print 'Done.'

    	
            


