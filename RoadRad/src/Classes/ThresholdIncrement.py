# This Python file uses the following encoding: utf-8

import os
import math
import shutil
import sys
import csv
import struct
import linecache
import ThresholdIncrementData as modulTIData

class ThresholdIncrement:
    
    #instance variables which define the relative paths
    octTempDirSuffix = '/TempOcts'
    radDirSuffix = '/Rads'
    radTempDirSuffix = '/TempRads'
    evalDirSuffix = '/Evaluation'
    lidcDirSuffix = '/LIDCs'
    
    #constructor
    def __init__( self, roadRadObject, path ):
    
        # retrieve working directory info
        self.xmlConfigPath = path
        self.xmlConfigName = 'SceneDescription.xml'
        # get RoadScene object from Evaluator
        self.roadScene = roadRadObject
        self.road = self.roadScene.scene.road
        self.lidcs = self.roadScene.lidcs.lidcs
        self.viewPoint = self.roadScene.targetParameters.viewPoint
        self.target = self.roadScene.targetParameters.target
        self.headlights = self.roadScene.headlights.headlights
        self.poles = self.roadScene.poles.poles
        # TI[] = measPoint, TI[][] = array of Lights, TI[][].Object = irradiance, theta, type, positionY, headlightType, position (left /right)
        self.tiArray = []
        self.numberOfMeasurementPoints = 10
        self.ageFactor = 0
        
        # start methods/functions
        self.calcMeasurementPoints( )
        self.makeMeasurementPosition( )
        self.makeRads( )
        self.makeOctsAndCalcIrradiance( )
        
        self.calcThetaAndMergeIrradiance( )
        self.calcAgeFactor( )
        #self.cleanLogs( )
    
    #---------------------------------------------------------------------------------------------------------------------
    # L_seq = (k * E_gl) / theta^n
    # E_gl illuminance of glare source
    # theta angle of glare source and exponent n
    # age factor k = 9.86 *(1+(Age/66.4)^4)
    # TI = 65 * (Lseq / L^0.8) in %
    # Lseq Schleierleuchtdichte, L mittlere Fahrbahnleuchtdichte
    # threshold increment = schwellenwerterhöhung
    #---------------------------------------------------------------------------------------------------------------------
    # L_seq = 10 * sum( E_k / theta_k ) mit k index für Leuchte und 10 für 23 Jahre alten Beobachter siehe oben k Faktor
    # abbruch1: innerhalb 500m --> poleArray.positionY < 500
    # abbruch2: wenn E_k < 2% sum(E_k) --> E_k / sum(E_k) < 0.02
    # bedingung1: Leuchten, die in einer Beobachtungsebene liegen, deren Winkel zur Horizontalen größer als
    # 20° ist, den Beobachter enthält und die Straße in Querrichtung kreuzt, müssen von der Berechnung
    # ausgenommen werden.
    # this equtation fits for 0,05 < mean Luminance of the road < 5 cd/m2 und 1,5 <theta_k <60 degrees .
    
    def calcMeasurementPoints( self ):
        # number of Measurement Points used in calcThetaAndMergeIrradiance() and makeMeasurementPosition()
        # according to DIN EN 13201 calculate necessary measures
        selectedArray = -1
        # select the first nonSingle pole
        for index, pole in enumerate( self.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if ( selectedArray == -1 ):
            print 'No Pole array defined, cannot position the object. terminating'
            sys.exit( 0 )   

        if( self.poles[ selectedArray ].spacing > 30 ):            
            while ( self.poles[ selectedArray ].spacing / self.numberOfMeasurementPoints ) > 3:
                self.numberOfMeasurementPoints = self.numberOfMeasurementPoints + 1
    
    def makeMeasurementPosition( self ):
        print 'Creating measurement position data'
        
        if( not os.path.isdir( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix )

        # fixed view direction for threshold increment ( TI )
        #view first to self.viewPoint.distance
        if ( self.viewPoint.viewDirection == 'first' ):
            ViewValueY = self.viewPoint.distance /  math.sqrt( self.viewPoint.distance**2 + self.viewPoint.height**2 )
            ViewValueZ = self.viewPoint.height / math.sqrt( self.viewPoint.distance**2 + self.viewPoint.height**2 )
            viewDirection ='0 ' + str( ViewValueY ) +' -' + str( ViewValueZ )
        
        #view last to self.roadScene.measFieldLength
        elif ( self.viewPoint.viewDirection == 'last' ):
            ViewValueY = ( self.viewPoint.distance + self.roadScene.measFieldLength ) /  math.sqrt( ( self.roadScene.measFieldLength + self.viewPoint.distance )**2 + self.viewPoint.height**2 )
            ViewValueZ = self.viewPoint.height / math.sqrt( ( self.roadScene.measFieldLength + self.viewPoint.distance )**2 + self.viewPoint.height**2 )
            viewDirection ='0 ' + str( ViewValueY ) +' -' + str( ViewValueZ )    
        
        #view fixed 1 degree by 1.45 height and 83 distance (RP800)
        else:
            viewDirection = '0 0.999847 -0.017467' 
        
        positionX = self.road.laneWidth * ( self.roadScene.targetParameters.target.onLane + 0.5 )
        positionZ = self.viewPoint.height
        
        print '    view direction: ' + str( viewDirection )
        print '    z-position of the observer: ' + str( positionZ ) 
        print '    x-position of the observer: ' + str( positionX )
        print '    measurement step width: ' + str( self.roadScene.measurementStepWidth ) 
        
        fTI = open( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTI.pos', "w" )
        
        for measPointNumber in range( self.numberOfMeasurementPoints ):
            positionY =  ( measPointNumber * self.roadScene.measurementStepWidth ) - self.viewPoint.distance
            print '    ' + str( measPointNumber ) + '-y-position of the observer: ' + str( positionY )
            viewPoint = '{0} {1} {2} '.format( positionX, positionY, positionZ )
            fTI.write( str( viewPoint ) + str( viewDirection ) + ' \n' )
        
        fTI.close( )
    
    def makeRads( self ):
        # generating rads for threshold Increment
        # includes thresholdIncremnt Log with viewposition, Ev and theta
        # DEBUG viewposition of DIN13201 is not the same like RP800!!!
        # problem with headlights L_mean_road only with fixed headlight not variable!!!
        print 'Generating: temporary rads for TI Calculation'
        
        if( not os.path.isdir( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix )
        
        for index, poleArray in enumerate( self.poles ):
            if( poleArray.isSingle == True ):
                if( ( poleArray.positionY < 500 ) and ( ( self.viewPoint.distance + poleArray.positionY ) > 0 ) ):
                    f = open( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix + '/single_' + str( index ) + '.rad', "w+" )
                    f.write( '######lights_s.rad######\n' )
                    if( poleArray.side == 'Left' ):
                        f.write( '!xform -t -' + str( self.road.sidewalkWidth ) + ' ' + str( poleArray.positionY ) + ' 0 ' + self.xmlConfigPath + ThresholdIncrement.radDirSuffix + '/' + poleArray.lidc + '_' + str( index )  + '_light_pole.rad\n' )
                    elif( poleArray.side == 'Right' ):
                        f.write( '!xform -rz -180 -t ' + str( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth )+' ' + str( poleArray.positionY ) + ' 0 ' + self.xmlConfigPath + ThresholdIncrement.radDirSuffix + '/' + poleArray.lidc + '_' + str( index ) + '_light_pole.rad\n' )
                    f.close( )
            elif( poleArray.isSingle == False ):
                for poleCounter in range( self.roadScene.numberOfLightsPerArray  ):
                    minDistance = ( ( -self.roadScene.numberOfLightsBeforeMeasurementArea + poleCounter ) * poleArray.spacing ) + self.viewPoint.distance
                    if( ( ( poleCounter * poleArray.spacing ) < 500 )  and ( minDistance > 0 ) ):
                        f = open( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix + '/array_' + str( index ) + '_' +  str( poleCounter ) + '.rad', "w+" )
                        if( poleArray.side == 'Left' ):
                            if ( poleArray.isStaggered == True ):
                                f.write( '!xform  -t -' + str( self.road.sidewalkWidth ) + ' ' + str( minDistance - self.viewPoint.distance + ( 0.5 * poleArray.spacing ) ) + ' 0 ' + self.xmlConfigPath + ThresholdIncrement.radDirSuffix + '/' + poleArray.lidc + '_' + str( index )  + '_light_pole.rad\n' )
                            else:
                                f.write( '!xform -t -' + str( self.road.sidewalkWidth ) + ' ' + str( minDistance - self.viewPoint.distance ) + ' 0 ' + self.xmlConfigPath + ThresholdIncrement.radDirSuffix + '/' + poleArray.lidc + '_' + str( index )  + '_light_pole.rad\n' )
                        elif( poleArray.side == 'Right' ):
                            if ( poleArray.isStaggered == True ):
                                f.write( '!xform -rz -180 -t ' + str( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth ) + ' ' + str( minDistance - self.viewPoint.distance + ( 0.5 * poleArray.spacing ) ) + ' 0 ' + self.xmlConfigPath + ThresholdIncrement.radDirSuffix + '/' + poleArray.lidc + '_' + str( index )  + '_light_pole.rad\n' )
                            else:
                                f.write( '!xform -rz -180 -t ' + str( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth ) + ' ' + str( minDistance - self.viewPoint.distance ) + ' 0 ' + self.xmlConfigPath + ThresholdIncrement.radDirSuffix + '/' + poleArray.lidc + '_' + str( index )  + '_light_pole.rad\n' )
        
        # generating headlight rad
        # mean luminance on road is only with fixed headlight position, fixed target distance is not running!
        if( self.headlights.__len__() > 0 ):
            print '    detected headlights'
            for index, headlightArray in enumerate( self.headlights ):
                if( headlightArray.lightDirection == 'opposite' ):
                    if( headlightArray.headlightDistanceMode == 'fixedHeadlightPosition' ):
                        left = open( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix + '/headlight_left_fixed_' + str( index ) + '.rad', "w+" )
                        left.write( "######headlightLeft.rad######\n" )
                        left.write( "!xform -n oppositeH_" + str( index ) + " -rx -" + str( 90.0 - headlightArray.slopeAngle ) + " -t " + str( self.road.laneWidth * ( headlightArray.onLane + 0.5 ) - ( headlightArray.width / 2 ) ) + " " + str( headlightArray.distance + self.roadScene.measFieldLength ) + " " + str( headlightArray.height ) + " " + self.xmlConfigPath + ThresholdIncrement.lidcDirSuffix + "/" + headlightArray.lidc + ".rad\n\n" )
                        left.close( )
                        
                        right = open( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix + '/headlight_right_fixed_' + str( index ) + '.rad', "w+" )
                        right.write( "######headlightRight.rad######\n" )
                        right.write( "!xform -n oppositeH_" + str( index ) + " -rx -" + str( 90.0 - headlightArray.slopeAngle ) + " -t " + str( self.road.laneWidth * ( headlightArray.onLane + 0.5 ) + ( headlightArray.width / 2 ) ) + " " + str( headlightArray.distance + self.roadScene.measFieldLength ) + " " + str( headlightArray.height ) + " " + self.xmlConfigPath + ThresholdIncrement.lidcDirSuffix + "/" + headlightArray.lidc + ".rad\n\n" )
                        right.close( )
                        
                        print '    fixed headlight ' + str( index + 1 ) + ' rad generated'
                    else:
                        for measPointNumber in range( self.numberOfMeasurementPoints ):
                            left = open( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix + '/headlight_left_var_' + str( index ) + '_' + str( measPointNumber ) + '.rad', "w+" )
                            left.write( "######headlightLeft.rad######\n" )
                            left.write( "!xform -n oppositeH_" + str( index ) + " -rx -" + str( 90.0 - headlightArray.slopeAngle ) + " -t " + str( self.road.laneWidth * ( headlightArray.onLane + 0.5 ) - ( headlightArray.width / 2 ) ) + " " + str( headlightArray.distance + self.roadScene.measFieldLength - ( measPointNumber * self.roadScene.measurementStepWidth )) + " " + str( headlightArray.height ) + " " + self.xmlConfigPath + ThresholdIncrement.lidcDirSuffix + "/" + headlightArray.lidc + ".rad\n\n" )
                            left.close( )
                            
                            right = open( self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix + '/headlight_right_var_' + str( index ) + '_' + str( measPointNumber ) + '.rad', "w+" )
                            right.write( "######headlightRight.rad######\n" )
                            right.write( "!xform -n oppositeH_" + str( index ) + " -rx -" + str( 90.0 - headlightArray.slopeAngle ) + " -t " + str( self.road.laneWidth * ( headlightArray.onLane + 0.5 ) + ( headlightArray.width / 2 ) ) + " " + str( headlightArray.distance + self.roadScene.measFieldLength - ( measPointNumber * self.roadScene.measurementStepWidth )) + " " + str( headlightArray.height ) + " " + self.xmlConfigPath + ThresholdIncrement.lidcDirSuffix + "/" + headlightArray.lidc + ".rad\n\n" )
                            right.close( )
                            
                            print '    variable headlight ' + str( index + 1 ) + ' on position ' + str( measPointNumber ) + ' rad generated'
                else:
                    print '    headlight ' + str( index + 1 ) + ' ignored - only opposite direction'
        
        print '    done ...'
        print ''
        
    def makeOctsAndCalcIrradiance( self ):
        print 'Generating Octs from TempRads'
        
        if( not os.path.isdir( self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix )
        
        for index, poleArray in enumerate( self.poles ):
            if( poleArray.isSingle == True ):
                if( ( poleArray.positionY < 500 ) and ( ( self.viewPoint.distance + poleArray.positionY ) > 0 ) ): 
                    cmd = 'oconv {0}/materials.rad {0}/road.rad {3}/single_{1}.rad {0}/night_sky.rad > {2}/tiScene_single_{1}.oct'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, index, self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix, self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix )
                    os.system( cmd )
                    print '    generated oct singlePole# ' + str( index )
                    cmd1 = "rtrace -h -I+ -w -ab 0 " + self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix + "/tiScene_single_" + str( index ) + ".oct < " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI_" + str( index ) + ".txt"
                    os.system( cmd1 )
                    print '    calculated Irradiance for given octree '
            elif( poleArray.isSingle == False ):
                for poleCounter in range( self.roadScene.numberOfLightsPerArray  ):
                    minDistance = ( ( -self.roadScene.numberOfLightsBeforeMeasurementArea + poleCounter ) * poleArray.spacing ) + self.viewPoint.distance
                    if( ( ( poleCounter * poleArray.spacing ) < 500 )  and ( minDistance > 0 ) ):
                        cmd = 'oconv {0}/materials.rad {0}/road.rad {3}/array_{1}_{4}.rad {0}/night_sky.rad > {2}/tiScene_array_{1}_{4}.oct'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, index, self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix, self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix, poleCounter )
                        os.system( cmd )
                        print '    generated oct arrayPole# ' + str( index ) + '_' + str( poleCounter )
                        cmd1 = "rtrace -h -I+ -w -ab 0 " + self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix + "/tiScene_array_" + str( index ) + "_" + str( poleCounter ) + ".oct < " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI_" + str( index ) + "_" + str( poleCounter ) + ".txt"
                        os.system( cmd1 )
                        print '    calculated Irradiance for given octree '
                        
        # oct tree for headlight
        if( self.headlights.__len__() > 0 ):
            for index, headlightArray in enumerate( self.headlights ):
                if( headlightArray.lightDirection == 'opposite' ):
                    if( headlightArray.headlightDistanceMode == 'fixedHeadlightPosition' ):
                        cmdLeft = 'oconv {0}/materials.rad {0}/road.rad {3}/headlight_left_fixed_{1}.rad {0}/night_sky.rad > {2}/tiScene_headlight_left_fixed_{1}.oct'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, index, self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix, self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix )
                        os.system( cmdLeft )
                        cmdRight = 'oconv {0}/materials.rad {0}/road.rad {3}/headlight_right_fixed_{1}.rad {0}/night_sky.rad > {2}/tiScene_headlight_right_fixed_{1}.oct'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, index, self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix, self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix )
                        os.system( cmdRight )
                        print '    generated fixed oct headlight# ' + str( index )
                        
                        cmd1Left = "rtrace -h -I+ -w -ab 0 " + self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix + "/tiScene_headlight_left_fixed_" + str( index ) + ".oct < " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTIHeadlightLeft_" + str( index ) + ".txt"
                        os.system( cmd1Left )
                        cmd1Right = "rtrace -h -I+ -w -ab 0 " + self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix + "/tiScene_headlight_right_fixed_" + str( index ) + ".oct < " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTIHeadlightRight_" + str( index ) + ".txt"
                        os.system( cmd1Right )
                        print '    calculated Irradiance for given octree '
                    else:
                        for measPointNumber in range( self.numberOfMeasurementPoints ):
                            cmdLeft = 'oconv {0}/materials.rad {0}/road.rad {3}/headlight_left_var_{1}_{4}.rad {0}/night_sky.rad > {2}/tiScene_headlight_left_var_{1}_{4}.oct'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, index, self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix, self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix, measPointNumber )
                            os.system( cmdLeft )
                            cmdRight = 'oconv {0}/materials.rad {0}/road.rad {3}/headlight_right_var_{1}_{4}.rad {0}/night_sky.rad > {2}/tiScene_headlight_right_var_{1}_{4}.oct'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, index, self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix, self.xmlConfigPath + ThresholdIncrement.radTempDirSuffix, measPointNumber )
                            os.system( cmdRight )
                            print '    generated var oct headlight# ' + str( index ) + ' on Position ' + str( measPointNumber )
                            
                            cmd1Left = "rtrace -h -I+ -w -ab 0 " + self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix + "/tiScene_headlight_left_var_" + str( index ) + "_" + str( measPointNumber ) + ".oct < " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTIHeadlightLeft_" + str( index ) + "_" + str( measPointNumber ) + ".txt"
                            os.system( cmd1Left )
                            cmd1Right = "rtrace -h -I+ -w -ab 0 " + self.xmlConfigPath + ThresholdIncrement.octTempDirSuffix + "/tiScene_headlight_right_var_" + str( index ) + "_" + str( measPointNumber ) + ".oct < " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTI.pos | rcalc -e '$1=179*($1*.265+$2*.67+$3*.065)' > " + self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + "/IrradianceTIHeadlightRight_" + str( index ) + "_" + str( measPointNumber ) + ".txt"
                            os.system( cmd1Right )
                            print '    calculated Irradiance for given octree '

        print '    done ...'
        print ''
        
    def calcThetaAndMergeIrradiance( self ):
        # theta for each light and viewposition
        print 'Calculating theta and Generating thresholdIncrementLog.txt'
        
        if( not os.path.isdir( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix )
                
        f = open( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/thresholdIncrementLog.txt', "w+" )
        f.write( 'measPoint view_x view_y view_z theta typ_light y_pos_luminaire E_v E_v/theta \n' )
        
        positionX = self.road.laneWidth * ( self.target.onLane + 0.5 )
        positionZ = self.viewPoint.height
        
        # self.viewPoint.distance nach DIN13201 = 2.75m nach RP800 = 83m
        for measPointNumber in range( self.numberOfMeasurementPoints ):
            rawLightArray = []
            # problem with merging data with irradianceTI.pos, loosing information 
            positionY =  ( measPointNumber * self.roadScene.measurementStepWidth ) - self.viewPoint.distance
            positionYFix = - self.viewPoint.distance
            for index, poleArray in enumerate( self.poles ):
                if( poleArray.isSingle == True ):
                    if( ( poleArray.positionY < 500 ) and ( ( poleArray.positionY - positionYFix ) > 0 ) ):
                        if( poleArray.side == 'Left' ):
                            poleDistance = math.sqrt( ( poleArray.positionY - positionY )**2 + ( positionX + self.road.sidewalkWidth - poleArray.overhang )**2 )
                        elif( poleArray.side == 'Right' ):
                            poleDistance = math.sqrt( ( poleArray.positionY - positionY )**2 + ( - positionX + 2.0 * self.road.laneWidth + self.road.sidewalkWidth - poleArray.overhang )**2 )
                        poleDiffHeight = math.fabs( poleArray.height - self.viewPoint.height )
                        thetaK = 90 -  math.degrees( math.atan( poleDistance / poleDiffHeight ) )
                        # get irradiance data from irradianceTI.txt
                        irradiance = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTI_' + str( index ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                        evTheta = irradiance / thetaK
                        # write data to thresholdIncrementLog
                        f.write( str( measPointNumber ) + ' ' + str( positionX ) + ' ' + str( positionY ) + ' ' + str( positionZ ) + ' ' + str( thetaK ) + ' single_' + str( index ) + ' ' + str( poleArray.positionY ) +  ' ' + str( irradiance ) +  ' ' + str( evTheta ) + '\n' )
                        # add new TIDataObject to rawLightArray
                        rawLightArray.append( modulTIData.ThresholdIncrementData( irradiance, thetaK, "light", poleArray.positionY - positionY, "", "" ) )
                elif( poleArray.isSingle == False ):
                    for poleCounter in range( self.roadScene.numberOfLightsPerArray  ):
                        # distances defined in DIN13201, 500m is from first light --> DEBUG: here from array beginning
                        # for staggered is different minDistance, BUT only use smallest one! ( 0.5 * poleArray.spacing ) + minDistance > 0 )
                        minDistance = ( ( -self.roadScene.numberOfLightsBeforeMeasurementArea + poleCounter ) * poleArray.spacing ) - positionY
                        minDistanceFix = ( ( -self.roadScene.numberOfLightsBeforeMeasurementArea + poleCounter ) * poleArray.spacing ) - positionYFix
                        if( ( ( poleCounter * poleArray.spacing ) < 500 ) and ( minDistanceFix > 0 ) ):
                            if( poleArray.side == 'Left' ):
                                if ( poleArray.isStaggered == True ):
                                    poleYDistance = ( 0.5 * poleArray.spacing ) + minDistance
                                    poleDistance = math.sqrt( ( poleYDistance )**2 + ( positionX + self.road.sidewalkWidth - poleArray.overhang )**2 )
                                else:
                                    poleYDistance = minDistance
                                    poleDistance = math.sqrt( ( poleYDistance )**2 + ( positionX + self.road.sidewalkWidth - poleArray.overhang )**2 )
                            elif( poleArray.side == 'Right' ):
                                if ( poleArray.isStaggered == True ):
                                    poleYDistance = ( 0.5 * poleArray.spacing ) + minDistance
                                    poleDistance = math.sqrt( ( poleYDistance )**2 + ( - positionX + 2.0 * self.road.laneWidth + self.road.sidewalkWidth - poleArray.overhang )**2 )
                                else:
                                    poleYDistance = minDistance
                                    poleDistance = math.sqrt( ( poleYDistance )**2 + ( - positionX + 2.0 * self.road.laneWidth + self.road.sidewalkWidth - poleArray.overhang  )**2 )
                                
                            poleDiffHeight = math.fabs( poleArray.height - self.viewPoint.height )
                            thetaK = 90 - math.degrees( math.atan( poleDistance / poleDiffHeight ) )
                            # get irradiance data from irradianceTI.txt
                            irradiance = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTI_' + str( index ) + '_' + str( poleCounter ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                            evTheta = irradiance / thetaK
                            # write data to thresholdIncrementLog
                            if ( ( thetaK > 20 ) or ( minDistance < 0 ) ):
                                print '    this theta is ignored: ' + "%.2f" % thetaK  + " with distance " + "%.2f" % minDistance
                            else:
                                f.write( str( measPointNumber ) + ' ' + str( positionX ) + ' ' + str( positionY ) + ' ' + str( positionZ ) + ' ' + str( thetaK ) + ' array_' + str( index ) + '_' + str( poleCounter ) + ' ' + str( poleYDistance + positionY ) +  ' ' + str( irradiance ) +  ' ' + str( evTheta ) + '\n' )
                                rawLightArray.append( modulTIData.ThresholdIncrementData( irradiance, thetaK, "light", poleYDistance, "", "" ) )

            # whats up with the headlights, here we go again!
            if( self.headlights.__len__() > 0 ):
                for index, headlightArray in enumerate( self.headlights ):
                    if( headlightArray.lightDirection == 'opposite' ):
                        
                        headlightLeftXDistance = math.fabs( self.target.onLane - headlightArray.onLane ) * self.road.laneWidth - ( headlightArray.width / 2 )
                        headlightRightXDistance = math.fabs( self.target.onLane - headlightArray.onLane ) * self.road.laneWidth + ( headlightArray.width / 2 )
                        poleDiffHeight = math.fabs( headlightArray.height - self.viewPoint.height )
                        
                        if( headlightArray.headlightDistanceMode == 'fixedHeadlightPosition' ):
                            headlightYDistance = headlightArray.distance + self.roadScene.measFieldLength - positionY
                            ## left headlight
                            
                            headlightLeftDistance = math.sqrt( ( headlightYDistance )**2 + ( headlightLeftXDistance )**2 )
                            thetaKLeft = 90 -  math.degrees( math.atan( headlightLeftDistance / poleDiffHeight ) )
                            
                            # get irradiance data from irradianceTIHeadlightLeft.txt
                            irradianceLeft = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTIHeadlightLeft_' + str( index ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                            evThetaLeft = irradianceLeft / thetaKLeft
                            f.write( str( measPointNumber ) + ' ' + str( positionX ) + ' ' + str( positionY ) + ' ' + str( positionZ ) + ' ' + str( thetaKLeft ) + ' headlight_left_fixed_' + str( index ) + ' ' + str( headlightYDistance + positionY ) +  ' ' + str( irradianceLeft ) +  ' ' + str( evThetaLeft ) + '\n' )
                            rawLightArray.append( modulTIData.ThresholdIncrementData( irradianceLeft, thetaKLeft, "headlight", ( headlightYDistance + positionY ), "fixed", "left" ) )
                            
                            ## right headlight
                            
                            headlightRightDistance = math.sqrt( ( headlightYDistance )**2 + ( headlightRightXDistance )**2 )
                            thetaKRight = 90 -  math.degrees( math.atan( headlightRightDistance / poleDiffHeight ) )
                            
                            # get irradiance data from irradianceTIHeadlightRight.txt
                            irradianceRight = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTIHeadlightRight_' + str( index ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                            evThetaRight = irradianceRight / thetaKRight
                            f.write( str( measPointNumber ) + ' ' + str( positionX ) + ' ' + str( positionY ) + ' ' + str( positionZ ) + ' ' + str( thetaKRight ) + ' headlight_right_fixed_' + str( index ) + ' ' + str( headlightYDistance + positionY ) +  ' ' + str( irradianceRight ) +  ' ' + str( evThetaRight ) + '\n' )
                            rawLightArray.append( modulTIData.ThresholdIncrementData( irradianceRight, thetaKRight, "headlight", ( headlightYDistance + positionY ), "fixed", "right" ) )
                        else:
                            # this "for-counter" is an idea of Jan, at every measPoint you have a driving car / but the result will be only a shift
                            # cause the variable distance of car and viewer has the same measurement stepwidth --> theta is shifted
                            # example: 
                            # measPos 1 60m distance carPos 2 40m distance = 100m
                            # measpos 2 55m distance carPos 1 45m distance = 100m
                            for fileCounter in range( self.numberOfMeasurementPoints ):
                                headlightYDistance = headlightArray.distance + self.roadScene.measFieldLength - positionY - ( fileCounter * self.roadScene.measurementStepWidth )
                                ## left headlight
                                
                                headlightLeftDistance = math.sqrt( ( headlightYDistance )**2 + ( headlightLeftXDistance )**2 )
                                thetaKLeft = 90 -  math.degrees( math.atan( headlightLeftDistance / poleDiffHeight ) )
                                # get irradiance data from irradianceTIHeadlight.txt
                                # only one value //irradiance = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTIHeadlight_' + str( index ) + '_' + str( measPointNumber ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                                irradianceLeft = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTIHeadlightLeft_' + str( index ) + '_' + str( fileCounter ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                                evThetaLeft = irradianceLeft / thetaKLeft
                                f.write( str( measPointNumber ) + ' ' + str( positionX ) + ' ' + str( positionY ) + ' ' + str( positionZ ) + ' ' + str( thetaKLeft ) + ' headlight_left_var_' + str( index ) + '_' + str( fileCounter ) + ' ' + str( headlightYDistance + positionY ) +  ' ' + str( irradianceLeft ) +  ' ' + str( evThetaLeft ) + '\n' )
                                rawLightArray.append( modulTIData.ThresholdIncrementData( irradianceLeft, thetaKLeft, "headlight", ( headlightYDistance + positionY ), "withTarget", "left" ) )
                                
                                ## right headlight
                                
                                headlightRightDistance = math.sqrt( ( headlightYDistance )**2 + ( headlightRightXDistance )**2 )
                                thetaKRight = 90 -  math.degrees( math.atan( headlightRightDistance / poleDiffHeight ) )
                                # get irradiance data from irradianceTIHeadlight.txt
                                # only one value //irradiance = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTIHeadlight_' + str( index ) + '_' + str( measPointNumber ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                                irradianceRight = float( linecache.getline( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix + '/IrradianceTIHeadlightRight_' + str( index ) + '_' + str( fileCounter ) + '.txt', measPointNumber + 1 ).rstrip('\n') )
                                evThetaRight = irradianceRight / thetaKRight
                                f.write( str( measPointNumber ) + ' ' + str( positionX ) + ' ' + str( positionY ) + ' ' + str( positionZ ) + ' ' + str( thetaKRight ) + ' headlight_right_var_' + str( index ) + '_' + str( fileCounter ) + ' ' + str( headlightYDistance + positionY ) +  ' ' + str( irradianceRight ) +  ' ' + str( evThetaRight ) + '\n' )
                                rawLightArray.append( modulTIData.ThresholdIncrementData( irradianceRight, thetaKRight, "headlight", ( headlightYDistance + positionY ), "withTarget", "right" ) )
        
            self.tiArray.append( rawLightArray )
        
        f.close()
        print '    used measurement points: ' + str ( len( self.tiArray ) )
        print '    lights at 1. measurement point: ' + str( len( self.tiArray[0] ) )
        print '    done ...'
        print ''
        
    def calcAgeFactor( self ):
        # age factor k = 9.86 *(1+(Age/66.4)^4)
        print 'Calculate age factor k for threshold increment'
        age = float( self.roadScene.scene.calculation.age )
        print '    viewers age: ' + str( age )
        self.ageFactor = 9.86 * ( 1.0 + ( age / 66.4 )**4 )
        print '    age factor: ' + "%.2f" % self.ageFactor 
        
    def cleanLogs( self ):
        # clean all unnecessary files
        for files in os.listdir( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix ):
            if ( files.startswith( 'IrradianceTI' ) ):
                file = "{0}/{1}".format( self.xmlConfigPath + ThresholdIncrement.evalDirSuffix, files )
                os.remove( file )
