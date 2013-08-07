# This Python file uses the following encoding: utf-8

import os
import math
import shutil
import sys
import csv
import struct

class ThresholdIncrement:
    
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
        #self.calcTI()
        self.calcVeilingLum( )
        #self.calcTheta( )
    
    # L_seq = (k * E_gl) / theta^n
    # E_gl illuminance of glare source
    # theta angle of glare source and exponent n
    # age factor k = 9.86 *(1+(Age/66.4)^4)
    # TI = 65 * (Lseq / L^0.8) in %
    # Lseq Schleierleuchtdichte, L mittlere Fahrbahnleuchtdichte
    # threshold increment = schwellenwerterh�hung
    def calcTI( self ):
        print 'Calculating threshold increment value'
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
            while ( self.poles[ selectedArray ].spacing / Evaluator.numberOfMeasurementPoints ) > 3:
                Evaluator.numberOfMeasurementPoints = Evaluator.numberOfMeasurementPoints + 1

        # fixed view direction for threshold increment ( TI )
        #view first to self.viewPoint.distance
        if self.viewPoint.viewDirection == 'first':
            ViewValueY = self.viewPoint.distance /  math.sqrt( self.viewPoint.distance**2 + self.viewPoint.height**2 )
            ViewValueZ = self.viewPoint.height / math.sqrt( self.viewPoint.distance**2 + self.viewPoint.height**2 )
            viewDirection ="0 " + str( ViewValueY ) +" -" + str( ViewValueZ )
        
        #view last to self.roadScene.measFieldLength
        elif self.viewPoint.viewDirection == 'last':
            ViewValueY = ( self.viewPoint.distance + self.roadScene.measFieldLength ) /  math.sqrt( ( self.roadScene.measFieldLength + self.viewPoint.distance )**2 + self.viewPoint.height**2 )
            ViewValueZ = self.viewPoint.height / math.sqrt( ( self.roadScene.measFieldLength + self.viewPoint.distance )**2 + self.viewPoint.height**2 )
            viewDirection ="0 " + str( ViewValueY ) +" -" + str( ViewValueZ )    
        
        #view fixed 1 degree by 1.45 height and 83 distance (RP800)
        else:
            viewDirection = "0 0.999847 -0.017467" 
        
        print '    view direction: ' + str( viewDirection )
        # fixed z position 
        print "    z-position of the observer: " + str( self.viewPoint.height ) 
        # fixed x position on given lane
        positionX = self.roadScene.scene.road.laneWidth * ( self.roadScene.targetParameters.target.onLane + 0.5 )
        print "    x-position of the observer: " + str( positionX )
        print '    measurement step width: ' + str( self.roadScene.measurementStepWidth ) 
        
        fTI = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/thresholdIncrement.pos', "w" )
        fTheta = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/thresholdIncrementTheta.txt', "w" )
        
        for measPointNumber in range( Evaluator.numberOfMeasurementPoints ):
            positionY =  ( measPointNumber * self.roadScene.measurementStepWidth ) - self.viewPoint.distance
            print "    " + str( measPointNumber ) + "-y-position of the observer: " + str( positionY )
            # calculate all theta_k's DIN 13201-3 ( TI ) for lights in 500m measurement area depend on positionY
            thetaK = 0.0
            for index, poleArray in enumerate( self.poles ):
                for poleCounter in range( self.roadScene.numberOfLightsPerArray  ):
                    if( poleArray.isSingle == True ):
                        if( poleArray.positionY < 500 ):
                            if( poleArray.side == 'Left' ):
                                poleDistance = math.sqrt( ( poleArray.positionY - positionY )**2 + ( positionX + self.roadScene.scene.road.sidewalkWidth - poleArray.overhang )**2 )
                            elif( poleArray.side == 'Right' ):
                                poleDistance = math.sqrt( ( poleArray.positionY - positionY )**2 + ( - positionX + self.roadScene.scene.road.laneWidth + self.roadScene.scene.road.sidewalkWidth - poleArray.overhang )**2 )
                            poleDiffHeight = poleArray.height - self.viewPoint.height
                            thetaK += math.atan( poleDiffHeight / poleDistance )
                    elif( poleArray.isSingle == False ):
                        if( ( poleCounter * poleArray.spacing ) < 500 ):
                            if( poleArray.side == 'Left' ):
                                poleDistance = math.sqrt( ( ( poleCounter * poleArray.spacing ) - positionY )**2 + ( positionX + self.roadScene.scene.road.sidewalkWidth - poleArray.overhang )**2 )
                            elif( poleArray.side == 'Right' ):
                                poleDistance = math.sqrt( ( ( poleCounter * poleArray.spacing ) - positionY )**2 + ( - positionX + self.roadScene.scene.road.laneWidth + self.roadScene.scene.road.sidewalkWidth - poleArray.overhang )**2 )
                            poleDiffHeight = poleArray.height - self.viewPoint.height
                            thetaK += math.atan( poleDiffHeight / poleDistance )
            
            viewPoint = '{0} {1} {2} '.format( positionX, positionY, self.viewPoint.height )

            fTI.write( str( viewPoint ) + str( viewDirection ) + ' \n' )
            fTheta.write( str( thetaK )  + ' \n' )
        
        fTI.close( )
        fTheta.close( )
        
        # calculate irradiance for TI 
        cmd1 = "rtrace -h -I+ -w -ab 1 " + self.xmlConfigPath + Evaluator.octDirSuffix + "/scene.oct < " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/thresholdIncrement.pos | rcalc -e ' $1=179*($1*.265+$2*.67+$3*.065) ' > " + self.xmlConfigPath + Evaluator.evalDirSuffix + "/thresholdIncrement.txt"
        os.system( cmd1 )

#DEBUG - Here #############################################    
#DEBUG - rtrace liefert gesamte Beleuchtungst�rke evt. alle winkel aufsummieren und dann teilen?
#DEBUG - thetaK in rcalc Schritt einbauen, aber thetaK pro Messchritt anders! Achtung! entweder Schleife oder extra Datei
#DEBUG - END ##############################################

    def calcVeilingLum( self ):
        # L_seq = 10 * sum( E_k / theta_k ) mit k index f�r Leuchte und 10 f�r 23 Jahre alten Beobachter siehe oben k Faktor
        # abbruch1: innerhalb 500m --> poleArray.positionY < 500
        # abbruch2: wenn E_k < 2% sum(E_k) --> E_k / sum(E_k) < 0.02
        # bedingung1: Leuchten, die in einer Beobachtungsebene liegen, deren Winkel zur Horizontalen gr��er als
        # 20� ist, den Beobachter enth�lt und die Stra�e in Querrichtung kreuzt, m�ssen von der Berechnung
        # ausgenommen werden.
        glareSources = 'findglare -vf {0}/eye.vp -c -r 4000 {1}/scene.oct > {2}/scene.glr'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, self.xmlConfigPath + ThresholdIncrement.octDirSuffix, self.xmlConfigPath + ThresholdIncrement.evalDirSuffix ) 
        os.system( glareSources )
        
        glareSourcesPic = 'findglare -vf {0}/eye.vp -c -r 4000 -p {1}/out_radiance.hdr > {2}/scenePic.glr'.format( self.xmlConfigPath + ThresholdIncrement.radDirSuffix, self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix, self.xmlConfigPath + ThresholdIncrement.evalDirSuffix ) 
        os.system( glareSourcesPic )