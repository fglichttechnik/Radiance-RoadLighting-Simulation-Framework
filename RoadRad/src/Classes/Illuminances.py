# This Python file uses the following encoding: utf-8

import os
import math
import shutil
import sys
import csv
import struct

class Illuminances:
    
    #instance variables which define the relative paths
    octDirSuffix = '/Octs'
    radDirSuffix = '/Rads'
    picDirSuffix = '/Pics'
    picSubDirSuffix = '/pics'
    evalDirSuffix = '/Evaluation'
    
    numberOfMeasurementRows = 3
    numberOfMeasurementPoints = 10
    
    #constructor
    def __init__( self, roadRadObject, path ):
    
        # retrieve working directory info
        self.xmlConfigPath = path
        self.xmlConfigName = "SceneDescription.xml"
        # get RoadScene object from Evaluator
        self.roadScene = roadRadObject
        self.viewPoint = self.roadScene.targetParameters.viewPoint
        self.headlights = self.roadScene.headlights.headlights
        self.poles = self.roadScene.poles.poles
        
        # start methods/functions
        self.calcIlluminances( )
        self.calcSideIlluminances( )
    
    #Prints view point files for every lane
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcIlluminances( self ):    
        
        print 'Generating: illuminance values at measurement points according to DIN EN 13201-3'
        
        #according to DIN EN 13201
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
            while ( self.poles[ selectedArray ].spacing / Illuminances.numberOfMeasurementPoints ) > 3:
                Illuminances.numberOfMeasurementPoints = Illuminances.numberOfMeasurementPoints + 1
        
    
        viewDirection = '0 0 1'
        positionZ = '0.02'
        
        while ( self.roadScene.scene.road.laneWidth / Illuminances.numberOfMeasurementRows ) > 1.5:
            Illuminances.numberOfMeasurementRows = Illuminances.numberOfMeasurementRows + 1
            
        print "    number of measurement points per lane: " + str( Illuminances.numberOfMeasurementPoints )
        print "    number of measurement rows per lane: " + str( Illuminances.numberOfMeasurementRows )
        print '    measurement step width: ' + str( self.roadScene.measurementStepWidth ) 
        
        f = open( self.xmlConfigPath + Illuminances.evalDirSuffix + '/illuminanceCoordinates.pos', "w" )
        l = open( self.xmlConfigPath + Illuminances.evalDirSuffix + '/illuminanceLanes.pos', "w" )
        
        for laneNumber in range( self.roadScene.scene.road.numLanes ):
            for rowNumber in range( Illuminances.numberOfMeasurementRows ):
                positionX = self.roadScene.scene.road.laneWidth * ( laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
                for measPointNumber in range( Illuminances.numberOfMeasurementPoints ):
                    positionY = ( ( measPointNumber + 0.5 ) * self.roadScene.measurementStepWidth )
                    viewPoint = '{0} {1} {2} '.format( positionX, positionY, positionZ )
                    f.write( str( viewPoint ) + str( viewDirection ) + ' \n' )
                    l.write( str( laneNumber) + ' ' + str( rowNumber ) + ' \n' )
                         
        f.close( )
        l.close( )
        
        cmd1 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Illuminances.octDirSuffix + "/scene.oct < " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/illuminanceCoordinates.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/rawIlluminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t  {0}/illuminanceLanes.pos {0}/illuminanceCoordinates.pos {0}/rawIlluminances.txt > {0}/illuminances.txt".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.system( cmd2 )
        with open( self.xmlConfigPath + Illuminances.evalDirSuffix + "/illuminances.txt", "r+" ) as illumfile:
             old = illumfile.read( ) # read everything in the file
             illumfile.seek( 0 ) # rewind
             illumfile.write( "measPoint_onLane measPoint_row viewPosition_x viewPosition_y viewPosition_z viewDirection_x viewDirection_y viewDirection_z illuminance\n" + old ) # write the new line before
        
        cmd3 = "{0}/illuminanceLanes.pos".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd3 )
        cmd4 = "{0}/illuminanceCoordinates.pos".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd4 )
        cmd4 = "{0}/rawIlluminances.txt".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd4 )
        
        print '    done ...'
        print ''
        
    #Prints view point files for left and right side
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcSideIlluminances( self ):    
        
        print 'Generating: illuminance values at left, right and upper side of measurementfield'
        #according to DIN EN 13201
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if selectedArray == -1:
            print "No Pole array defined, cannot position the object. terminating"
            sys.exit( 0 )   

        if( self.poles[ selectedArray ].spacing > 30 ):            
            while ( self.poles[ selectedArray ].spacing / Illuminances.numberOfMeasurementPoints ) > 3:
                Illuminances.numberOfMeasurementPoints = Illuminances.numberOfMeasurementPoints + 1

        # fixed view direction for illuminance
        viewDirectionLeftX = '1 0 0'
        viewDirectionRightX = '-1 0 0'
        viewDirectionUpperZ = '0 0 -1'
        
        # fixed x position depend on lane number and lane width
        positionLeftX = '0.02'
        positionRightX = ( self.roadScene.scene.road.numLanes * self.roadScene.scene.road.laneWidth ) - 0.02
        # fixed z position depend on the middle pole height
        allHeights = 0
        for entry in self.poles:
            allHeights += entry.height
            positionUpperZ = allHeights / self.poles.__len__()
        
        print "    x-position of the left sensor: " + str( positionLeftX )  
        print "    x-position of the right sensor: " + str( positionRightX ) 
        print "    z-position of the upper sensor: " + str( positionUpperZ )
        print '    measurement step width: ' + str( self.roadScene.measurementStepWidth ) 
        
        fLeft = open( self.xmlConfigPath + Illuminances.evalDirSuffix + '/illuminanceLeftSideCoordinates.pos', "w" )
        fRight = open( self.xmlConfigPath + Illuminances.evalDirSuffix + '/illuminanceRightSideCoordinates.pos', "w" )
        fUpper = open( self.xmlConfigPath + Illuminances.evalDirSuffix + '/illuminanceUpperSideCoordinates.pos', "w" )
        r = open( self.xmlConfigPath + Illuminances.evalDirSuffix + '/illuminanceRows.pos', "w" )
        
        for rowNumber in range( Illuminances.numberOfMeasurementRows ):
            # three z side position for illuminance at 0.66, 1.33 and 2 meters
            positionZ = ( rowNumber + 1 ) * positionUpperZ / Illuminances.numberOfMeasurementRows
            # three x upper position for illuminance at x = 25%, 50% and 75% lane width
            positionUpperX = self.roadScene.scene.road.laneWidth * self.roadScene.scene.road.numLanes * (( rowNumber + 1 ) * 0.25 ) 
            
            for measPointNumber in range( Illuminances.numberOfMeasurementPoints ):
                positionY = ( measPointNumber + 0.5 ) * self.roadScene.measurementStepWidth 
                
                viewPointLeft = '{0} {1} {2} '.format( positionLeftX, positionY, positionZ )
                viewPointRight = ' {0} {1} {2} '.format( positionRightX, positionY, positionZ )
                viewPointUpper = ' {0} {1} {2} '.format( positionUpperX, positionY, positionUpperZ )
                
                fLeft.write( str( viewPointLeft ) + str( viewDirectionLeftX ) + ' \n' )
                fRight.write( str( viewPointRight ) + str( viewDirectionRightX ) + ' \n' )
                fUpper.write( str( viewPointUpper ) + str( viewDirectionUpperZ ) + ' \n' )
                r.write( str( rowNumber ) + ' \n' )
                         
        fLeft.close( )
        fRight.close( )
        fUpper.close( )
        r.close( )
        
        # calculate left side 
        cmd1 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Illuminances.octDirSuffix + "/scene.oct < " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/illuminanceLeftSideCoordinates.pos | rcalc -e ' $1=179*($1*.265+$2*.67+$3*.065) ' > " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/rawLeftIlluminances.txt"
        os.system( cmd1 )
        
        # calculate right side
        cmd2 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Illuminances.octDirSuffix + "/scene.oct < " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/illuminanceRightSideCoordinates.pos | rcalc -e ' $1=179*($1*.265+$2*.67+$3*.065) ' > " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/rawRightIlluminances.txt"
        os.system( cmd2 )
        
        # calculate upper side
        cmd3 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Illuminances.octDirSuffix + "/scene.oct < " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/illuminanceUpperSideCoordinates.pos | rcalc -e ' $1=179*($1*.265+$2*.67+$3*.065) ' > " + self.xmlConfigPath + Illuminances.evalDirSuffix + "/rawUpperIlluminances.txt"
        os.system( cmd3 )
        
        # combine all txt files to one
        cmd4 = "rlam -t  {0}/illuminanceRows.pos {0}/illuminanceLeftSideCoordinates.pos {0}/rawLeftIlluminances.txt {0}/illuminanceRightSideCoordinates.pos {0}/rawRightIlluminances.txt {0}/illuminanceUpperSideCoordinates.pos {0}/rawUpperIlluminances.txt > {0}/sideIlluminances.txt".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.system( cmd4 )
        
        # add heading to the illuminance.txt table 
        with open( self.xmlConfigPath + Illuminances.evalDirSuffix + "/sideIlluminances.txt", "r+" ) as illumfile:
             old = illumfile.read( ) # read everything in the file
             illumfile.seek( 0 ) # rewind
             illumfile.write( "measPoint_Zrow viewPositionLeft_x viewPositionLeft_y viewPositionLeft_z viewDirectionLeft_x viewDirectionLeft_y viewDirectionLeft_z illuminanceLeft viewPositionRight_x viewPositionRight_y viewPositionRight_z viewDirectionRight_x viewDirectionRight_y viewDirectionRight_z illuminanceRight viewPositionUpper_x viewPositionUpper_y viewPositionUpper_z viewDirectionUpper_x viewDirectionUpper_y viewDirectionUpper_z illuminanceUpper\n" + old ) # write the new line before
        
        print "! Delete temporary illumninance files"
        
        # delete all useless txt files
        cmd5 = "{0}/illuminanceRows.pos".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd5 )
        cmd6 = "{0}/illuminanceLeftSideCoordinates.pos".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd6 )
        cmd6 = "{0}/illuminanceRightSideCoordinates.pos".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd6 )
        cmd6 = "{0}/illuminanceUpperSideCoordinates.pos".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd6 )
        cmd7 = "{0}/rawLeftIlluminances.txt".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd7 )
        cmd7 = "{0}/rawRightIlluminances.txt".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd7 )
        cmd7 = "{0}/rawUpperIlluminances.txt".format( self.xmlConfigPath + Illuminances.evalDirSuffix )
        os.remove( cmd7 )
        
        print '    done ...'
        print ''    