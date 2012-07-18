# This Python file uses the following encoding: utf-8

import os
from xml.dom.minidom import parse
import math
import shutil
import sys
import csv
import struct
import xml.dom as dom
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
        self.makePic( )
        #self.makeFalsecolor( )
        self.evalLuminance( )
        self.evalIlluminance( )
        self.makeXML( )
        self.checkStandards( )

        return
    
    #Scene description xml parser.
    def parseConfig( self ):
        print 'Begining to parse XML Config. for din evaluation'
        configfile = open( self.rootDirPath + "/SceneDescription.xml", 'r' )
        dom = parse( configfile )
        configfile.close( )
        
        descriptionDesc = dom.getElementsByTagName( 'Description' )
        if( descriptionDesc[0].attributes ):
            self.title = descriptionDesc[0].attributes["Title"].value
        
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
    
    	if( not os.path.isdir( self.rootDirPath + self.evalDirSuffix ) ):
            os.mkdir( self.rootDirPath + self.evalDirSuffix )   
		
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
    	
        f = open( self.workingDirPath + self.evalDirSuffix + '/luminanceCoordinates.pos', "w" )
        l = open( self.workingDirPath + self.evalDirSuffix + '/luminanceLanes.pos', "w" )
        
    	for laneInOneDirection in range( self.scene.NumLanes ):
    		
    		for laneNumber in range( self.scene.NumLanes ):   
    			
    			viewerXPosition = ( self.scene.LaneWidth * (laneInOneDirection + 0.5 ) )
    			viewPoint = '{0} {1} {2}'.format( viewerXPosition, viewerYPosition, viewerZPosition )
    			distanceOfMeasRows = self.scene.LaneWidth / 3
    			
    			for rowNumber in range( 3 ):
    				rowXPosition = self.scene.LaneWidth * (laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
    				directionX = rowXPosition - viewerXPosition
    				
    				for measPointNumber in range( self.numberOfMeasurementPoints ):
    					directionY = ( ( measPointNumber + 0.5 ) * self.measurementStepWidth ) - viewerYPosition
    					viewDirection = ' {0} {1} {2}'.format( directionX, directionY, directionZ )
    					
    					f.write( str( viewPoint ) + str( viewDirection ) + ' \n')
    					l.write( str( laneInOneDirection ) + ' ' + str( laneNumber ) + ' ' + str( rowNumber ) + ' \n' )
    		    		
  			
        		
        f.close( )
        l.close( )
        
        
        
        cmd1 = "rtrace -h -oo -od -ov " + self.workingDirPath + self.octDirSuffix + "/scene_din.oct < " + self.workingDirPath + self.evalDirSuffix + "/luminanceCoordinates.pos  | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.workingDirPath + self.evalDirSuffix + "/rawLuminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t {0}/luminanceLanes.pos {0}/luminanceCoordinates.pos {0}/rawLuminances.txt >  {0}/luminances.txt".format( self.workingDirPath + self.evalDirSuffix )
        os.system( cmd2 )
        with open( self.workingDirPath + self.evalDirSuffix + "/luminances.txt", "r+" ) as illumfile:
     		old = illumfile.read() # read everything in the file
     		illumfile.seek(0) # rewind
     		illumfile.write("viewer_onLane measPoint_onLane measPoint_row viewPosition_x viewPosition_y viewPosition_z viewDirection_x viewDirection_y viewDirection_z luminance\n" + old) # write the new line before
        cmd3 = "{0}/luminanceLanes.pos".format( self.workingDirPath + self.evalDirSuffix )
        os.remove( cmd3 )
        cmd4 = "{0}/luminanceCoordinates.pos".format( self.workingDirPath + self.evalDirSuffix )
        os.remove( cmd4 )
        cmd4 = "{0}/rawLuminances.txt".format( self.workingDirPath + self.evalDirSuffix )
        os.remove( cmd4 )
        
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
    	
    	f = open( self.workingDirPath + self.evalDirSuffix + '/illuminanceCoordinates.pos', "w" )
    	l = open( self.workingDirPath + self.evalDirSuffix + '/illuminanceLanes.pos', "w" )
    	
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
        
        cmd1 = "rtrace -h -I+ -w -ab 1 " + self.rootDirPath + self.octDirSuffix + "/scene_din.oct < " + self.workingDirPath + self.evalDirSuffix + "/illuminanceCoordinates.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.workingDirPath + self.evalDirSuffix + "/rawIlluminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t  {0}/illuminanceLanes.pos {0}/illuminanceCoordinates.pos {0}/rawIlluminances.txt > {0}/illuminances.txt".format( self.workingDirPath + self.evalDirSuffix )
        os.system( cmd2 )
        with open( self.workingDirPath + self.evalDirSuffix + "/illuminances.txt", "r+" ) as illumfile:
     		old = illumfile.read() # read everything in the file
     		illumfile.seek(0) # rewind
     		illumfile.write("measPoint_onLane measPoint_row viewPosition_x viewPosition_y viewPosition_z viewDirection_x viewDirection_y viewDirection_z illuminance\n" + old) # write the new line before
        
        cmd3 = "{0}/illuminanceLanes.pos".format( self.workingDirPath + self.evalDirSuffix )
        os.remove( cmd3 )
        cmd4 = "{0}/illuminanceCoordinates.pos".format( self.workingDirPath + self.evalDirSuffix )
        os.remove( cmd4 )
        cmd4 = "{0}/rawIlluminances.txt".format( self.workingDirPath + self.evalDirSuffix )
        os.remove( cmd4 )
        
        
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
    	L_m_ = []
    	L_min_ = []
    	U_0_ = []
    	U_l_ = []
    	
    	for laneInOneDirection in range( self.scene.NumLanes ):
    		
    		print 'Viewer on lane number: ' + str( laneInOneDirection )
    		
    		L_m = 0
    		L_min__ = []
    		L_l_min_ = []
    		L_l_m_ = []
    		
    		
    		for lane in range( self.scene.NumLanes ):
    			print '	lane: ' + str( lane )
    			lumFile = open( self.workingDirPath + self.evalDirSuffix + '/luminances.txt', 'r')
    			lumReader = csv.reader( lumFile, delimiter = ' ' )
    			headerline = lumReader.next()
    			
    			L = []
    			L_l = []
    			
    			L_m_lane = 0
    			L_l_m_lane = 0
    			
    			L_m_values = 0
    			L_l_values = 0
    			
    			for row in lumReader:
    				if( float( row[1] ) == float( lane ) ) and ( float( row[0] )== float( laneInOneDirection ) ):
    					L_row = float( row[9] )
    					L_m_lane += float( row[9] )
    					L_m_values += 1
    					L.append( L_row)
    					
    					if( float( row[2] ) == 1 ):
    						L_l_row = float( row[9] )
    						L_l_values += 1
    						L_l_m_lane += float( row[9] )
    						L_l.append( L_l_row )
    						
    			L_m = L_m + (L_m_lane / L_m_values )
    			L_m_lane = L_m_lane / L_m_values
    			L_min_lane = min( L )
    			L_max_lane = max( L )
    			L_min__.append( L_min_lane )
    			U_0__ = L_min_lane / L_m_lane 
    			
    			print '		L_m of lane ' + str( lane ) + ':			' + str( L_m_lane )
    			print '		L_min of lane ' + str( lane ) + ':		' + str( L_min__[lane] )
    			print '		L_max of lane ' + str( lane ) + ':		' + str( L_max_lane )
    			print '		U_0 of lane ' + str( lane ) + ':			' + str( U_0__)
    			
    			L_l_m_.append( L_l_m_lane / L_l_values )
    			L_l_m_lane = L_l_m_lane / L_l_values
    			L_l_min_lane = min( L_l )
    			L_l_min_.append( L_l_min_lane )
    			U_l_.append( L_l_min_lane / L_l_m_lane )
    			
    			print '		L_m lengthwise of lane ' + str( lane ) + ':	' + str( L_l_m_lane )
    			print '		L_min lengthwise of lane ' + str( lane ) + ':	' + str( L_l_min_[lane] )
    			print '		L_max lengthwise of lane ' + str( lane ) + ':	' + str( max( L_l ) )
    			print '		U_l of lane ' + str( lane ) + ':			' + str( U_l_[lane] )
    			
    			lumFile.close( )
    		
    		L_m = L_m / self.scene.NumLanes
    		L_m_.append( L_m )
    		L_min_ = min( L_min__ )
    		U_0_.append( L_min_ / L_m )
    		U_l = min( U_l_ )
    		
    		print '	L_m = ' + str( L_m )
    		print '	L_min = ' + str( L_min_ )
    		print '	L_max = ' + str( max( L ) )
    		print '	U_0 = ' + str( L_min_ / L_m )
    		print '	U_l = ' + str( U_l )
    	
       	self.meanLuminance = min( L_m_ )
        self.uniformityOfLuminance = min( U_0_)
        self.lengthwiseUniformityOfLuminance = min( U_l_ )
        
        print 'L_m = ' + str( self.meanLuminance )
    	print 'L_min = ' + str( min( L_min__ ) )
    	print 'L_max = ' + str( max( L ) )
    	print 'U_0 = ' + str( min( U_0_) )
    	print 'U_l = ' + str( min( U_l_ ) )
        
        print "Done."			
        
    def evalIlluminance( self ):
    	print 'Evaluate illuminances...'    	    	
    	
    	E_min_ = []
    	E_m_ = 0
    	g_1_ = []
    	    	
    	for lane in range( self.scene.NumLanes ):
    		print '	lane: ' + str( lane )
    		lumFile = open( self.workingDirPath + self.evalDirSuffix + '/illuminances.txt', 'r')
    		lumReader = csv.reader( lumFile, delimiter = ' ' )
    		headerline = lumReader.next()
    		
    		E = []    		
    		E_m_lane = 0    		
    		E_m_values = 0
    		
    		for row in lumReader:
    			if( float( row[0] ) == float( lane ) ):
    				E_row = float( row[8] )
    				E_m_lane += float( row[8] )
    				E_m_values += 1
    				E.append( E_row)
    		
    		E_m_ = E_m_ + ( E_m_lane / E_m_values )
    		E_m_lane = E_m_lane / E_m_values
    		E_min_lane = min( E )
    		E_min_.append( E_min_lane )
    		g_1_.append( E_min_lane / E_m_lane )
    		
    		print '		E_m of lane ' + str( lane ) + ':			' + str( E_m_lane )
    		print '		E_min of lane ' + str( lane ) + ':		' + str( E_min_[lane] )
    		print '		E_max of lane ' + str( lane ) + ':		' + str( max( E ) )
    		print '		g_1 of lane ' + str( lane ) + ':			' + str( g_1_[lane] )
    		
    		lumFile.close( )
        		
		E_m = E_m_ / self.scene.NumLanes
		E_min = min( E_min_ )
        g_1 = E_min / E_m
        
        print '	E_m = ' + str( E_m )
        print '	E_min = ' + str( E_min)
        print '	E_max = ' + str( max( E ) )
        print '	g_1 = ' + str( g_1 )
        
        self.meanIlluminance = E_m
        self.minIlluminance = E_min        
        self.uniformityOfIlluminance = g_1
        
        print "Done."	
    
    
    def makeXML( self ):
    		print 'Generating XML: file..'
    		if( not os.path.isdir( self.rootDirPath + self.evalDirSuffix ) ):
    			os.mkdir( self.rootDirPath + self.evalDirSuffix )
    		
    		implement = dom.getDOMImplementation( )
    		doc = implement.createDocument( None, 'Evaluation', None );
    		
    		descr_element = doc.createElement( "Description" )
    		descr_element.setAttribute( "Title", self.title )
    		doc.documentElement.appendChild( descr_element )
    		
    		lum_element = doc.createElement( "Luminance" )
    		doc.documentElement.appendChild( lum_element )
    		
    		meanLum_element = doc.createElement( "meanLuminance" )
    		meanLum_element.setAttribute( "Lm", str( self.meanLuminance ) )
    		lum_element.appendChild( meanLum_element )
    		
    		uniformityLum_element = doc.createElement( "uniformityOfLuminance" )
    		uniformityLum_element.setAttribute( "U0", str( self.uniformityOfLuminance ) )
    		lum_element.appendChild( uniformityLum_element )
    		
    		lengthUniformityLum_element = doc.createElement( "lengthwiseUniformityOfLuminance" )
    		lengthUniformityLum_element.setAttribute( "Ul", str( self.lengthwiseUniformityOfLuminance ) )
    		lum_element.appendChild( lengthUniformityLum_element )
    		
    		illum_element = doc.createElement( "Illuminance" )
    		doc.documentElement.appendChild( illum_element )
    		
    		meanIllum_element = doc.createElement( "meanIlluminance" )
    		meanIllum_element.setAttribute( "Em", str( self.meanIlluminance ) )
    		illum_element.appendChild( meanIllum_element )
    		
    		minIllum_element = doc.createElement( "minIlluminance" )
    		minIllum_element.setAttribute( "Emin", str( self.minIlluminance ) )
    		illum_element.appendChild( minIllum_element )
    		
    		uniformityIllum_element = doc.createElement( "uniformityOfIlluminance" )
    		uniformityIllum_element.setAttribute( "g1", str( self.uniformityOfIlluminance ) )
    		illum_element.appendChild( uniformityIllum_element )
    		
    		f = open( self.rootDirPath + self.evalDirSuffix + '/Evaluation.xml', "w" )
    		doc.writexml( f, "\n", "	")
    		f.close( )   		
    		
    		print 'Done.'
    		
    def checkStandards( self ):
		print 'Check DIN EN 13201-2 classes...'
			
		checktree = parse( os.getcwd() + "/Standard_classes.xml" )
		for node in checktree.getElementsByTagName( 'ME-Class' ):
			Lm = node.getAttribute( 'Lm' )
			U0 = node.getAttribute( 'U0' )
			Ul = node.getAttribute( 'Ul' )
			
			if( float( self.meanLuminance ) >= float( Lm ) and float( self.uniformityOfLuminance ) >= float( U0 ) and float( self.lengthwiseUniformityOfLuminance ) >= float( Ul ) ):
				lumDIN = node.getAttribute( 'name' )
				break
			else:
				lumDIN = 'None'
				continue
				
		print '	ME-Class fullfillment: 	' + str( lumDIN )
		
		evaltree = parse( self.rootDirPath + self.evalDirSuffix + '/Evaluation.xml' )
		child1 = evaltree.createElement( "ClassFullfillment" )
		child1.setAttribute( "class", lumDIN )
		node1 = evaltree.getElementsByTagName( 'Luminance')
		node1.item(0).appendChild( child1 )
		
		
		for node in checktree.getElementsByTagName( 'S-Class' ):
			Em = node.getAttribute( 'Em' )
			Emin = node.getAttribute( 'Emin' )
			g1 = node.getAttribute( 'g1' )
			
			if( float( self.meanIlluminance ) >= float( Em ) and float( self.minIlluminance ) >= float( Emin ) ):
				illumDIN = node.getAttribute( 'name' )
				break
			else:
				illumDIN = 'None'
				continue
		
		print '	S-Class fullfillment: 	' + str( illumDIN	)
		
	
		child2 = evaltree.createElement( "ClassFullfillment" )
		child2.setAttribute( "class", illumDIN )
		node2 = evaltree.getElementsByTagName( 'Illuminance')
		node2.item(0).appendChild( child2 )
		
		child3 = evaltree.createElement( "UniformityCriteria" )
		child3.setAttribute( "true", "Yes" )		
		if ( float( self.uniformityOfIlluminance ) < float( g1 ) ):
			print '				Uniformity criteria not fullfilled! '
			child3.setAttribute( "true", "No" )			
		node3 = evaltree.getElementsByTagName( 'Illuminance')
		node3.item(0).appendChild( child3 )
			
		
		f = open( self.rootDirPath + self.evalDirSuffix + '/Evaluation.xml', "w" )
		evaltree.writexml( f, "\n", "	")
		f.close( )
		
		print 'Done.'

    	
            


