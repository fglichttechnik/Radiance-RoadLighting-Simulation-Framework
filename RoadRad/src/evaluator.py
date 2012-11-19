# This Python file uses the following encoding: utf-8

import os
import math
import shutil
import sys
import csv
import struct
import xml.dom as dom
from xml.dom.minidom import parse
import Classes.RoadScene as modulRoadscene


#write a few documentation
class Evaluator:
    
    #instance variables which define the relative paths
    octDirSuffix = '/Octs'
    radDirSuffix = '/Rads'
    picDirSuffix = '/Pics'
    picSubDirSuffix = '/pics'
    evalDirSuffix = '/Evaluation'
    
    #output image resolution
    horizontalRes = 1380
    verticalRes = 1030

    numberOfMeasurementRows = 3
    numberOfMeasurementPoints = 10
    meanLuminance = 0.0
    uniformityOfLuminance = 0.0
    lengthwiseUniformityOfLuminance = 0.0
    meanIlluminance = 0.0
    minIlluminance = 0.0
    uniformityOfIlluminance = 0.0
    
    def __init__( self, path ):
        
        # retrieve working directory info
        self.xmlConfigPath = path
        self.xmlConfigName = "SceneDescription.xml"
        # initialize XML as RoadScene object
        self.roadScene = modulRoadscene.RoadScene( self.xmlConfigPath, self.xmlConfigName )
        
        self.makeOct( )
        self.calcLuminances( )
        self.calcIlluminances( )
        self.calcSideIlluminances( )
        self.makePic( )
        #self.makeFalsecolor( )
        self.evalLuminance( )
        self.evalIlluminance( )
        self.evalSideIlluminance( )
        self.makeXML( )
        self.checkStandards( )

    
    #system call to radiance framework to generate oct files out of the various rads
    # both for the actual simulated image and the refernce pictures to determine the 
    # pixel position of the target objects
    def makeOct( self ):
        if( not os.path.isdir( self.xmlConfigPath + Evaluator.octDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Evaluator.octDirSuffix )        
        
        #make oct for scene without targets for din evaluation
        if self.roadScene.headlights.__len__() > 0:
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/headlight.rad {0}/night_sky.rad > {1}/scene_din.oct'.format( self.xmlConfigPath + Evaluator.radDirSuffix, self.xmlConfigPath + Evaluator.octDirSuffix )
            os.system(cmd)
        else:    
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/night_sky.rad > {1}/scene_din.oct'.format( self.xmlConfigPath + Evaluator.radDirSuffix, self.xmlConfigPath + Evaluator.octDirSuffix )
            os.system(cmd)
            
    #Prints view point files for every lane
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcLuminances( self ):
    
        if( not os.path.isdir( self.xmlConfigPath + Evaluator.evalDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Evaluator.evalDirSuffix )   
        
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.roadScene.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if selectedArray == -1:
            print "No Pole array defined, cannot position the object. terminating"
            sys.exit( 0 )   

        if( self.roadScene.poles[ selectedArray ].spacing > 30 ):            
            while ( self.roadScene.poles[ selectedArray ].spacing / Evaluator.numberOfMeasurementPoints ) > 3:
                Evaluator.numberOfMeasurementPoints = Evaluator.numberOfMeasurementPoints + 1
        
        print 'Generating: luminance values according to DIN EN 13201-3'
        print '    number of measurement points: ' + str( Evaluator.numberOfMeasurementPoints )
        self.roadScene.measurementStepWidth = self.roadScene.measFieldLength / Evaluator.numberOfMeasurementPoints        
        print '    measurement step width: ' + str( self.roadScene.measurementStepWidth ) 
        print '    measurment field length: ' + str( self.roadScene.measFieldLength )

        
    
        directionZ = 0 - self.roadScene.targetParameters.viewPoint.height   
        viewerYPosition = - self.roadScene.targetParameters.viewPoint.distance
        viewerZPosition = self.roadScene.targetParameters.viewPoint.height
        
        # open writable position files
        f = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/luminanceCoordinates.pos', "w" )
        l = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/luminanceLanes.pos', "w" )
        
        for laneInOneDirection in range( self.roadScene.scene.road.numLanes ):
            for laneNumber in range( self.roadScene.scene.road.numLanes ):   
                
                # middle viewer x-position for every lane 
                viewerXPosition = ( self.roadScene.scene.road.laneWidth * ( laneInOneDirection + 0.5 ) )
                viewPoint = '{0} {1} {2}'.format( viewerXPosition, viewerYPosition, viewerZPosition )
                distanceOfMeasRows = self.roadScene.scene.road.laneWidth / 3
                
                # three x-position per lanewidth on x = 25%, 50% and 75% 
                for rowNumber in range( 3 ):
                    rowXPosition = self.roadScene.scene.road.laneWidth * ( laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
                    directionX = rowXPosition - viewerXPosition
                    
                    for measPointNumber in range( Evaluator.numberOfMeasurementPoints ):
                        directionY = ( ( measPointNumber + 0.5 ) * self.roadScene.measurementStepWidth ) - viewerYPosition
                        viewDirection = ' {0} {1} {2}'.format( directionX, directionY, directionZ )
                        
                        # write data to luminanceCoordinates and luminanceLanes.pos
                        f.write( str( viewPoint ) + str( viewDirection ) + ' \n')
                        l.write( str( laneInOneDirection ) + ' ' + str( laneNumber ) + ' ' + str( rowNumber ) + ' \n' )
                                    
        f.close( )
        l.close( )
        
        cmd1 = "rtrace -h -oo -od -ov " + self.xmlConfigPath + Evaluator.octDirSuffix + "/scene_din.oct < " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/luminanceCoordinates.pos  | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/rawLuminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t {0}/luminanceLanes.pos {0}/luminanceCoordinates.pos {0}/rawLuminances.txt >  {0}/luminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.system( cmd2 )
        with open( self.xmlConfigPath + Evaluator.evalDirSuffix + "/luminances.txt", "r+" ) as illumfile:
             old = illumfile.read() # read everything in the file
             illumfile.seek(0) # rewind
             illumfile.write("viewer_onLane measPoint_onLane measPoint_row viewPosition_x viewPosition_y viewPosition_z viewDirection_x viewDirection_y viewDirection_z luminance\n" + old) # write the new line before
        cmd3 = "{0}/luminanceLanes.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd3 )
        cmd4 = "{0}/luminanceCoordinates.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd4 )
        cmd4 = "{0}/rawLuminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd4 )
        
        print "Done."
        
    #Prints view point files for every lane
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcIlluminances( self ):    
        
        print 'Generating: illuminance values at measurement points according to DIN EN 13201-3'
        
        #according to DIN EN 13201
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.roadScene.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if selectedArray == -1:
            print "No Pole array defined, cannot position the object. terminating"
            sys.exit( 0 )   

        if( self.roadScene.poles[ selectedArray ].spacing > 30 ):            
            while ( self.roadScene.poles[ selectedArray ].spacing / Evaluator.numberOfMeasurementPoints ) > 3:
                Evaluator.numberOfMeasurementPoints = Evaluator.numberOfMeasurementPoints + 1
        
    
        viewDirection = '0 0 1'
        positionZ = '0.02'
        
        while ( self.roadScene.scene.road.laneWidth / Evaluator.numberOfMeasurementRows ) > 1.5:
            Evaluator.numberOfMeasurementRows = Evaluator.numberOfMeasurementRows + 1
            
        print "    number of measurement points per lane: " + str( Evaluator.numberOfMeasurementPoints )
        print "    number of measurement rows per lane: " + str( Evaluator.numberOfMeasurementRows )
        
        f = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/illuminanceCoordinates.pos', "w" )
        l = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/illuminanceLanes.pos', "w" )
        
        for laneNumber in range( self.roadScene.scene.road.numLanes ):
            for rowNumber in range( Evaluator.numberOfMeasurementRows ):
                positionX = self.roadScene.scene.road.laneWidth * ( laneNumber + ( ( rowNumber + 1 ) * 0.25 ) )
                for measPointNumber in range( Evaluator.numberOfMeasurementPoints ):
                    positionY = ( ( measPointNumber + 0.5 ) * self.roadScene.measurementStepWidth )
                    viewPoint = '{0} {1} {2} '.format( positionX, positionY, positionZ )
                    f.write( str( viewPoint ) + str( viewDirection ) + ' \n' )
                    l.write( str( laneNumber) + ' ' + str( rowNumber ) + ' \n' )
                         
        f.close( )
        l.close( )
        
        cmd1 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Evaluator.octDirSuffix + "/scene_din.oct < " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/illuminanceCoordinates.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/rawIlluminances.txt"
        os.system( cmd1 )
        cmd2 = "rlam -t  {0}/illuminanceLanes.pos {0}/illuminanceCoordinates.pos {0}/rawIlluminances.txt > {0}/illuminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.system( cmd2 )
        with open( self.xmlConfigPath + Evaluator.evalDirSuffix + "/illuminances.txt", "r+" ) as illumfile:
             old = illumfile.read() # read everything in the file
             illumfile.seek(0) # rewind
             illumfile.write("measPoint_onLane measPoint_row viewPosition_x viewPosition_y viewPosition_z viewDirection_x viewDirection_y viewDirection_z illuminance\n" + old) # write the new line before
        
        cmd3 = "{0}/illuminanceLanes.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd3 )
        cmd4 = "{0}/illuminanceCoordinates.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd4 )
        cmd4 = "{0}/rawIlluminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd4 )
        
        print "Done."
    
    #Prints view point files for left and right side
    #Based on the viewpoint mode, one of several viewpoints are written
    def calcSideIlluminances( self ):    
        
        print 'Generating: illuminance values at left, right and upper side of measurementfield'
        #according to DIN EN 13201
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.roadScene.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if selectedArray == -1:
            print "No Pole array defined, cannot position the object. terminating"
            sys.exit( 0 )   

        if( self.roadScene.poles[ selectedArray ].spacing > 30 ):            
            while ( self.roadScene.poles[ selectedArray ].spacing / Evaluator.numberOfMeasurementPoints ) > 3:
                Evaluator.numberOfMeasurementPoints = Evaluator.numberOfMeasurementPoints + 1

        # fixed view direction for illuminance
        viewDirectionLeftX = '1 0 0'
        viewDirectionRightX = '-1 0 0'
        viewDirectionUpperZ = '0 0 -1'
        
        # fixed x position depend on lane number and lane width
        positionLeftX = '0.02'
        positionRightX = ( self.roadScene.scene.road.numLanes * self.roadScene.scene.road.laneWidth ) - 0.02
        # fixed z position depend on the middle pole height
        allHeights = 0
        for entry in self.roadScene.poles:
            allHeights += entry.height
            positionUpperZ = allHeights / self.roadScene.poles.__len__()
        
        print "    x-position of the left sensor: " + str( positionLeftX )  
        print "    x-position of the right sensor: " + str( positionRightX ) 
        print "    z-position of the upper sensor: " + str( positionUpperZ ) 
        
        fLeft = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/illuminanceLeftSideCoordinates.pos', "w" )
        fRight = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/illuminanceRightSideCoordinates.pos', "w" )
        fUpper = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/illuminanceUpperSideCoordinates.pos', "w" )
        r = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/illuminanceRows.pos', "w" )
        
        for rowNumber in range( Evaluator.numberOfMeasurementRows ):
            # three z side position for illuminance at 0.66, 1.33 and 2 meters
            positionZ = ( rowNumber + 1 ) * positionUpperZ / Evaluator.numberOfMeasurementRows
            # three x upper position for illuminance at x = 25%, 50% and 75% lane width
            positionUpperX = self.roadScene.scene.road.laneWidth * self.roadScene.scene.road.numLanes * (( rowNumber + 1 ) * 0.25 ) 
            
            for measPointNumber in range( Evaluator.numberOfMeasurementPoints ):
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
        cmd1 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Evaluator.octDirSuffix + "/scene_din.oct < " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/illuminanceLeftSideCoordinates.pos | rcalc -e ' $1=179*($1*.265+$2*.67+$3*.065) ' > " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/rawLeftIlluminances.txt"
        os.system( cmd1 )
        
        # calculate right side
        cmd2 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Evaluator.octDirSuffix + "/scene_din.oct < " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/illuminanceRightSideCoordinates.pos | rcalc -e ' $1=179*($1*.265+$2*.67+$3*.065) ' > " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/rawRightIlluminances.txt"
        os.system( cmd2 )
        
        # calculate upper side
        cmd3 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Evaluator.octDirSuffix + "/scene_din.oct < " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/illuminanceUpperSideCoordinates.pos | rcalc -e ' $1=179*($1*.265+$2*.67+$3*.065) ' > " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/rawUpperIlluminances.txt"
        os.system( cmd3 )
        
        # combine all txt files to one
        cmd4 = "rlam -t  {0}/illuminanceRows.pos {0}/illuminanceLeftSideCoordinates.pos {0}/rawLeftIlluminances.txt {0}/illuminanceRightSideCoordinates.pos {0}/rawRightIlluminances.txt {0}/illuminanceUpperSideCoordinates.pos {0}/rawUpperIlluminances.txt > {0}/sideIlluminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.system( cmd4 )
        
        # add heading to the illuminance.txt table 
        with open( self.xmlConfigPath + Evaluator.evalDirSuffix + "/sideIlluminances.txt", "r+" ) as illumfile:
             old = illumfile.read() # read everything in the file
             illumfile.seek(0) # rewind
             illumfile.write("measPoint_Zrow viewPositionLeft_x viewPositionLeft_y viewPositionLeft_z viewDirectionLeft_x viewDirectionLeft_y viewDirectionLeft_z illuminanceLeft viewPositionRight_x viewPositionRight_y viewPositionRight_z viewDirectionRight_x viewDirectionRight_y viewDirectionRight_z illuminanceRight viewPositionUpper_x viewPositionUpper_y viewPositionUpper_z viewDirectionUpper_x viewDirectionUpper_y viewDirectionUpper_z illuminanceUpper\n" + old) # write the new line before
        
        print "Delete temporary illumninance files"
        
        # delete all useless txt files
        cmd5 = "{0}/illuminanceRows.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd5 )
        cmd6 = "{0}/illuminanceLeftSideCoordinates.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd6 )
        cmd6 = "{0}/illuminanceRightSideCoordinates.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd6 )
        cmd6 = "{0}/illuminanceUpperSideCoordinates.pos".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd6 )
        cmd7 = "{0}/rawLeftIlluminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd7 )
        cmd7 = "{0}/rawRightIlluminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd7 )
        cmd7 = "{0}/rawUpperIlluminances.txt".format( self.xmlConfigPath + Evaluator.evalDirSuffix )
        os.remove( cmd7 )
        
        print "Done."
    
    def makePic(self):
            if( not os.path.isdir( self.xmlConfigPath + Evaluator.picDirSuffix ) ):
                os.mkdir( self.xmlConfigPath + Evaluator.picDirSuffix )
            if( not os.path.isdir( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix ) ):
                os.mkdir( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix )              
            
            #make pic without target for later evaluation
            print 'out_radiance.hdr'
            if self.roadScene.targetParameters.viewPoint.targetDistanceMode == 'fixedViewPoint':
                cmd1 = 'rpict -vtv -vf {2}/eye.vp -x {3} -y {4} {0}/scene_din.oct > {1}/out_radiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
                os.system( cmd1 )
            else:
                cmd1 = 'rpict -vtv -vf {2}/eye0.vp -x {3} -y {4} {0}/scene_din.oct > {1}/out_radiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
                os.system( cmd1 )
            print 'out_irradiance.hdr'
            if self.roadScene.targetParameters.viewPoint.targetDistanceMode == 'fixedViewPoint':
                cmd2 = 'rpict -i -vtv -vf {2}/eye.vp -x {3} -y {4} {0}/scene_din.oct > {1}/out_irradiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
                os.system( cmd2 )
            else:
                cmd2 = 'rpict -i -vtv -vf {2}/eye0.vp -x {3} -y {4} {0}/scene_din.oct > {1}/out_irradiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
                os.system( cmd2 )
            
    def makeFalsecolor( self ):
            print 'falsecolor_luminance.hdr'
            cmd0 = 'falsecolor -i {0}/out_radiance.hdr -log 5 -l cd/m^2 > {0}/falsecolor_luminance.hdr'.format( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix )
            os.system( cmd0 )
            print 'falsecolor_illuminance.hdr'
            cmd1 = 'falsecolor -i {0}/out_irradiance.hdr -log 5 -l lx > {0}/falsecolor_illuminance.hdr'.format( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix )
            os.system( cmd1 )
                
    
    def evalLuminance( self ):
    
        print 'Evaluate luminances...'
        L_m_ = []
        L_min_ = []
        U_0_ = []
        U_l_ = []
        
        for laneInOneDirection in range( self.roadScene.scene.road.numLanes ):
            
            print 'Viewer on lane number: ' + str( laneInOneDirection )
            
            L_m = 0
            L_min__ = []
            L_l_min_ = []
            L_l_m_ = []
             
            for lane in range( self.roadScene.scene.road.numLanes ):
                print '    lane: ' + str( lane )
                lumFile = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/luminances.txt', 'r')
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
                
                print '        L_m of lane ' + str( lane ) + ':            ' + str( L_m_lane )
                print '        L_min of lane ' + str( lane ) + ':        ' + str( L_min__[lane] )
                print '        L_max of lane ' + str( lane ) + ':        ' + str( L_max_lane )
                print '        U_0 of lane ' + str( lane ) + ':            ' + str( U_0__)
                
                L_l_m_.append( L_l_m_lane / L_l_values )
                L_l_m_lane = L_l_m_lane / L_l_values
                L_l_min_lane = min( L_l )
                L_l_min_.append( L_l_min_lane )
                U_l_.append( L_l_min_lane / L_l_m_lane )
                
                print '        L_m lengthwise of lane ' + str( lane ) + ':    ' + str( L_l_m_lane )
                print '        L_min lengthwise of lane ' + str( lane ) + ':    ' + str( L_l_min_[lane] )
                print '        L_max lengthwise of lane ' + str( lane ) + ':    ' + str( max( L_l ) )
                print '        U_l of lane ' + str( lane ) + ':            ' + str( U_l_[lane] )
                
                lumFile.close( )
            
            L_m = L_m / self.roadScene.scene.road.numLanes
            L_m_.append( L_m )
            L_min_ = min( L_min__ )
            U_0_.append( L_min_ / L_m )
            U_l = min( U_l_ )
            
            print '    L_m = ' + str( L_m )
            print '    L_min = ' + str( L_min_ )
            print '    L_max = ' + str( max( L ) )
            print '    U_0 = ' + str( L_min_ / L_m )
            print '    U_l = ' + str( U_l )
        
        Evaluator.meanLuminance = min( L_m_ )
        Evaluator.uniformityOfLuminance = min( U_0_)
        Evaluator.lengthwiseUniformityOfLuminance = min( U_l_ )
        
        print 'L_m = ' + str( Evaluator.meanLuminance )
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
                
        for lane in range( self.roadScene.scene.road.numLanes ):
            print '    lane: ' + str( lane )
            lumFile = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/illuminances.txt', 'r')
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
                    E.append( E_row )
            
            E_m_ = E_m_ + ( E_m_lane / E_m_values )
            E_m_lane = E_m_lane / E_m_values
            E_min_lane = min( E )
            E_min_.append( E_min_lane )
            g_1_.append( E_min_lane / E_m_lane )
            
            print '        E_m of lane ' + str( lane ) + ':            ' + str( E_m_lane )
            print '        E_min of lane ' + str( lane ) + ':        ' + str( E_min_[lane] )
            print '        E_max of lane ' + str( lane ) + ':        ' + str( max( E ) )
            print '        g_1 of lane ' + str( lane ) + ':            ' + str( g_1_[lane] )
            
            lumFile.close( )
                
        E_m = E_m_ / self.roadScene.scene.road.numLanes
        E_min = min( E_min_ )
        g_1 = E_min / E_m
        
        print '    E_m = ' + str( E_m )
        print '    E_min = ' + str( E_min)
        print '    E_max = ' + str( max( E ) )
        print '    g_1 = ' + str( g_1 )
        
        Evaluator.meanIlluminance = E_m
        Evaluator.minIlluminance = E_min        
        Evaluator.uniformityOfIlluminance = g_1
        
        print "Done."    
        
    def evalSideIlluminance( self ):
        print 'Evaluate side and upper illuminances...'                
        
        # average side and upper illuminance
        E_m_SideLeft_ = 0
        E_m_SideRight_ = 0
        E_m_SideUpper_ = 0
                
        lumFile = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/sideIlluminances.txt', 'r')
        lumReader = csv.reader( lumFile, delimiter = ' ' )
        headerline = lumReader.next()
        
        E_Left = []
        E_Right = []
        E_Upper = []
        E_m_lane_Left = 0
        E_m_lane_Right = 0
        E_m_lane_Upper = 0
        E_m_values = 0
        
        for Zrow in range(3):
            for row in lumReader:
                if( float( row[0] ) == float( Zrow ) ):
                    E_Left_row = float( row[7] )
                    E_Right_row = float( row[14] )
                    E_Upper_row = float( row[21] )
                    E_m_lane_Left += float( row[7] )
                    E_m_lane_Right += float( row[14] )
                    E_m_lane_Upper += float( row[21] )
                    E_m_values += 1
                    E_Left.append( E_Left_row )
                    E_Right.append( E_Right_row )
                    E_Upper.append( E_Upper_row )
        
            E_m_SideLeft_ = E_m_SideLeft_ + ( E_m_lane_Left / E_m_values )
            E_m_lane_Left = E_m_lane_Left / E_m_values
            E_m_SideRight_ = E_m_SideRight_ + ( E_m_lane_Right / E_m_values )
            E_m_lane_Right = E_m_lane_Right / E_m_values
            E_m_SideUpper_ = E_m_SideUpper_ + ( E_m_lane_Upper / E_m_values )
            E_m_lane_Upper = E_m_lane_Upper / E_m_values
        
            print '        E_m of left z position ' + str( Zrow ) + ':            ' + str( E_m_lane_Left )
            print '        E_m of right z position ' + str( Zrow ) + ':            ' + str( E_m_lane_Right )
            print '        E_m of upper x position ' + str( Zrow ) + ':            ' + str( E_m_lane_Upper )
        
        lumFile.close( )
                
        E_m_SideLeft = E_m_SideLeft_ / 3.0
        E_m_SideRight = E_m_SideRight_ / 3.0
        E_m_SideUpper = E_m_SideUpper_ / 3.0
        
        print '    E_m_Left = ' + str( E_m_SideLeft )
        print '    E_m_Right = ' + str( E_m_SideRight )
        print '    E_m_Upper = ' + str( E_m_SideUpper )
        
        Evaluator.meanIlluminanceLeft = E_m_SideLeft
        Evaluator.meanIlluminanceRight = E_m_SideRight
        Evaluator.meanIlluminanceUpper = E_m_SideUpper
        print "Done."    
    
    def makeXML( self ):
            print 'Generating XML: file..'
            if( not os.path.isdir( self.xmlConfigPath + Evaluator.evalDirSuffix ) ):
                os.mkdir( self.xmlConfigPath + Evaluator.evalDirSuffix )
            
            implement = dom.getDOMImplementation( )
            doc = implement.createDocument( None, 'Evaluation', None );
            
            descr_element = doc.createElement( "Description" )
            descr_element.setAttribute( "Title", self.roadScene.scene.description.title )
            doc.documentElement.appendChild( descr_element )
            
            lum_element = doc.createElement( "Luminance" )
            doc.documentElement.appendChild( lum_element )
            
            meanLum_element = doc.createElement( "meanLuminance" )
            meanLum_element.setAttribute( "Lm", str( Evaluator.meanLuminance ) )
            lum_element.appendChild( meanLum_element )
            
            uniformityLum_element = doc.createElement( "uniformityOfLuminance" )
            uniformityLum_element.setAttribute( "U0", str( Evaluator.uniformityOfLuminance ) )
            lum_element.appendChild( uniformityLum_element )
            
            lengthUniformityLum_element = doc.createElement( "lengthwiseUniformityOfLuminance" )
            lengthUniformityLum_element.setAttribute( "Ul", str( Evaluator.lengthwiseUniformityOfLuminance ) )
            lum_element.appendChild( lengthUniformityLum_element )
            
            illum_element = doc.createElement( "Illuminance" )
            doc.documentElement.appendChild( illum_element )
            
            meanIllum_element = doc.createElement( "meanIlluminance" )
            meanIllum_element.setAttribute( "Em", str( Evaluator.meanIlluminance ) )
            meanIllum_element.setAttribute( "Em_Left", str( Evaluator.meanIlluminanceLeft ) )
            meanIllum_element.setAttribute( "Em_Right", str( Evaluator.meanIlluminanceRight ) )
            meanIllum_element.setAttribute( "Em_Upper", str( Evaluator.meanIlluminanceUpper ) )
            illum_element.appendChild( meanIllum_element )
            
            minIllum_element = doc.createElement( "minIlluminance" )
            minIllum_element.setAttribute( "Emin", str( Evaluator.minIlluminance ) )
            illum_element.appendChild( minIllum_element )
            
            uniformityIllum_element = doc.createElement( "uniformityOfIlluminance" )
            uniformityIllum_element.setAttribute( "g1", str( Evaluator.uniformityOfIlluminance ) )
            illum_element.appendChild( uniformityIllum_element )
            
            f = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/Evaluation.xml', "w" )
            doc.writexml( f, "\n", "    ")
            f.close( )           
            
            print 'Done.'
            
    def checkStandards( self ):
        print 'Check DIN EN 13201-2 classes...'
            
        checktree = parse( os.getcwd() + "/Standard_classes.xml" )
        for node in checktree.getElementsByTagName( 'ME-Class' ):
            Lm = node.getAttribute( 'Lm' )
            U0 = node.getAttribute( 'U0' )
            Ul = node.getAttribute( 'Ul' )
            
            if( float( Evaluator.meanLuminance ) >= float( Lm ) and float( Evaluator.uniformityOfLuminance ) >= float( U0 ) and float( Evaluator.lengthwiseUniformityOfLuminance ) >= float( Ul ) ):
                lumDIN = node.getAttribute( 'name' )
                break
            else:
                lumDIN = 'None'
                continue
                
        print '    ME-Class fullfillment:     ' + str( lumDIN )
        
        evaltree = parse( self.xmlConfigPath + Evaluator.evalDirSuffix + '/Evaluation.xml' )
        child1 = evaltree.createElement( "ClassFullfillment" )
        child1.setAttribute( "class", lumDIN )
        node1 = evaltree.getElementsByTagName( 'Luminance')
        node1.item(0).appendChild( child1 )
        
        
        for node in checktree.getElementsByTagName( 'S-Class' ):
            Em = node.getAttribute( 'Em' )
            Emin = node.getAttribute( 'Emin' )
            g1 = node.getAttribute( 'g1' )
            
            if( float( Evaluator.meanIlluminance ) >= float( Em ) and float( Evaluator.minIlluminance ) >= float( Emin ) ):
                illumDIN = node.getAttribute( 'name' )
                break
            else:
                illumDIN = 'None'
                continue
        
        print '    S-Class fullfillment:     ' + str( illumDIN )
        
    
        child2 = evaltree.createElement( "ClassFullfillment" )
        child2.setAttribute( "class", illumDIN )
        node2 = evaltree.getElementsByTagName( 'Illuminance')
        node2.item(0).appendChild( child2 )
        
        child3 = evaltree.createElement( "UniformityCriteria" )
        child3.setAttribute( "true", "Yes" )        
        if ( float( Evaluator.uniformityOfIlluminance ) < float( g1 ) ):
            print '                Uniformity criteria not fullfilled! '
            child3.setAttribute( "true", "No" )            
        node3 = evaltree.getElementsByTagName( 'Illuminance')
        node3.item(0).appendChild( child3 )
            
        
        f = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/Evaluation.xml', "w" )
        evaltree.writexml( f, "\n", "    ")
        f.close( )
        
        print 'Done.'