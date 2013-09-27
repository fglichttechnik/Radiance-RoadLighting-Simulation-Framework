# This Python file uses the following encoding: utf-8

import os
import math
import shutil
import sys
import csv
import struct

class Luminances:
    
    #instance variables which define the relative paths
    octDirSuffix = '/Octs'
    evalDirSuffix = '/Evaluation'

    numberOfMeasurementRows = 3
    numberOfMeasurementPoints = 10
    
    #constructor
    def __init__( self, roadRadObject, path ):
        
        #modulEvaluator.Evaluator.__init__( self, path )
        
        # retrieve working directory info
        self.xmlConfigPath = path
        self.xmlConfigName = "SceneDescription.xml"
        # get RoadScene object from Evaluator
        self.roadScene = roadRadObject
        self.viewPoint = self.roadScene.targetParameters.viewPoint
        self.poles = self.roadScene.poles.poles
        
        # start methods/functions
        self.calcLuminances( )
    
    #Prints view point files for every lane
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcLuminances( self ):
    
        if( not os.path.isdir( self.xmlConfigPath + Luminances.evalDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Luminances.evalDirSuffix )   
        
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if( selectedArray == -1 ):
            print "No Pole array defined, cannot position the object. terminating"
            sys.exit( 0 )   

        if( self.poles[ selectedArray ].spacing > 30 ):            
            while ( self.poles[ selectedArray ].spacing / Luminances.numberOfMeasurementPoints ) > 3:
                Luminances.numberOfMeasurementPoints = Luminances.numberOfMeasurementPoints + 1
        
        self.roadScene.measurementStepWidth = self.roadScene.measFieldLength / Luminances.numberOfMeasurementPoints
        
        print 'Generating: luminance values according to DIN EN 13201-3'
        print '    number of measurement points: ' + str( Luminances.numberOfMeasurementPoints )
        print '    measurement step width: ' + str( self.roadScene.measurementStepWidth ) 
        print '    measurment field length: ' + str( self.roadScene.measFieldLength )

        directionZ = 0 - self.roadScene.targetParameters.viewPoint.height   
        viewerYPosition = - self.roadScene.targetParameters.viewPoint.distance
        viewerZPosition = self.roadScene.targetParameters.viewPoint.height
        
        # open writable position files
        f = open( self.xmlConfigPath + Luminances.evalDirSuffix + '/luminanceCoordinates.pos', "w" )
        l = open( self.xmlConfigPath + Luminances.evalDirSuffix + '/luminanceLanes.pos', "w" )
        
        for laneInOneDirection in range( self.roadScene.scene.road.numLanes ):
            for laneNumber in range( self.roadScene.scene.road.numLanes ):   
                
                # middle viewer x-position for every lane 
                viewerXPosition = ( self.roadScene.scene.road.laneWidth * ( laneInOneDirection + 0.5 ) )
                viewPoint = '{0} {1} {2}'.format( viewerXPosition, viewerYPosition, viewerZPosition )
                
                # three x-position per lanewidth on x = 25%, 50% and 75% 
                for rowNumber in range( 3 ):
                    rowXPosition = self.roadScene.scene.road.laneWidth * ( laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
                    directionX = rowXPosition - viewerXPosition
                    
                    for measPointNumber in range( Luminances.numberOfMeasurementPoints ):
                        directionY = ( ( measPointNumber + 0.5 ) * self.roadScene.measurementStepWidth ) - viewerYPosition
                        viewDirection = ' {0} {1} {2}'.format( directionX, directionY, directionZ )
                        
                        # write data to luminanceCoordinates and luminanceLanes.pos
                        f.write( str( viewPoint ) + str( viewDirection ) + ' \n')
                        l.write( str( laneInOneDirection ) + ' ' + str( laneNumber ) + ' ' + str( rowNumber ) + ' \n' )
                                    
        f.close( )
        l.close( )
        
        cmd1 = "rtrace -h -oo -od -ov " + self.xmlConfigPath + Luminances.octDirSuffix + "/scene.oct < " + self.xmlConfigPath + Luminances.evalDirSuffix + "/luminanceCoordinates.pos  | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + Luminances.evalDirSuffix + "/rawLuminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t {0}/luminanceLanes.pos {0}/luminanceCoordinates.pos {0}/rawLuminances.txt >  {0}/luminances.txt".format( self.xmlConfigPath + Luminances.evalDirSuffix )
        os.system( cmd2 )
        with open( self.xmlConfigPath + Luminances.evalDirSuffix + "/luminances.txt", "r+" ) as illumfile:
             old = illumfile.read( ) # read everything in the file
             illumfile.seek( 0 ) # rewind
             illumfile.write("viewer_onLane measPoint_onLane measPoint_row viewPosition_x viewPosition_y viewPosition_z viewDirection_x viewDirection_y viewDirection_z luminance\n" + old) # write the new line before
        cmd3 = "{0}/luminanceLanes.pos".format( self.xmlConfigPath + Luminances.evalDirSuffix )
        os.remove( cmd3 )
        cmd4 = "{0}/luminanceCoordinates.pos".format( self.xmlConfigPath + Luminances.evalDirSuffix )
        os.remove( cmd4 )
        cmd4 = "{0}/rawLuminances.txt".format( self.xmlConfigPath + Luminances.evalDirSuffix )
        os.remove( cmd4 )
        
        print '    done ...'
        print ''