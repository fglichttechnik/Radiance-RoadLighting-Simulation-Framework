# This Python file uses the following encoding: utf-8

import sys
import os
import math
import Scene as modulScene
import TargetParameters as modulTargetParameters
import Headlights as modulHeadlights
import LIDCs as modulLIDCs
import Poles as modulPoles
from lxml import etree

class RoadScene:
    
    verticalAngle = 0                       # calculated by calcOpeningAngle and focalLnegth
    horizontalAngle = 0                     # calculated by calcOpeningAngle and focalLnegth
    sceneLength = 8000                      # length of road !important for ambient calculation was 240000        
    sidewalkHeight = 0.1                    # height of sidewalk
    markingWidth = 0.1                      # dashLine width
    markingLength = 4                       # dashLine length
    poleRadius = 0.05                       # radius of pole cylinder
    numberOfLightsPerArray = 9              # was 4
    numberOfLightsBeforeMeasurementArea = 3 # was 1
    measurementStartPosition = 0            # calculated by calcMeasurementField
    measurementStepWidth = 0                # calculated by calcMeasurementField
    measFieldLength = 0                     # calculated by calcMeasurementField with pole spacing and numPoleFields
    lidcRotation = -90                      # was -90
    sensorHeight = 8.9                      # in mm
    sensorWidth = 6.64                      # in mm
    
    ## constructor
    def __init__( self, xmlfilePath, xmlfileName ):
        # retrieve working directory info
        self.workingDirPath = xmlfilePath
        self.sceneDecriptor = xmlfileName
        
        # check xml 
        self.parseWithValidation_xml( 'SceneDescription.dtd' )

        # initialize objects from roadscene
        self.scene = modulScene.Scene( self.root )
        self.targetParameters = modulTargetParameters.TargetParameters( self.root )
        self.lidcs = modulLIDCs.LIDCs( self.root )
        self.headlights = modulHeadlights.Headlights( self.root )
        self.poles = modulPoles.Poles( self.root )
        
        self.checkSenseOfParameters( )

        self.calcMeasurementField( )
        self.calcOpeningAngle( )
    
    ## Validate a given XML file with a given external DTD with error report
    def parseWithValidation_xml( self, dtd_filename ):
        print 'Begining to validate XML File.'
        print '    xml Filename: ' + str( self.sceneDecriptor )
        print '    dtd Filename: ' + str( dtd_filename )
        
        dtd = etree.DTD( dtd_filename )
        configfile = self.workingDirPath + '/' + self.sceneDecriptor 
        self.root = etree.parse( configfile )

        if not( dtd.validate( self.root ) ):
            print( dtd.error_log.filter_from_errors( )[ 0 ] )
            sys.exit( 0 )
        else:
            print '    xml is valid'
            print '------------------------------------------------------'
    
    ## check parameters of xml are senseless        
    def checkSenseOfParameters( self ):
    	#check if the scene parameter 'numlane' and 'target lane' make sense
        if( self.scene.road.numLanes - self.targetParameters.target.onLane < 1 ):
            print 'Numlanes and TargetPosition Parameters are impossible'
            sys.exit( 0 )

    ## calculate the measuremnt area of the road scene
    def calcMeasurementField( self ):
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.poles.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if selectedArray == -1:
            print 'No Pole array defined, cannot position the object. terminating'
            sys.exit( 0 )             
            
        #according to DIN EN 13201 / RP 8 00 (max 5 m)
        RoadScene.measFieldLength = self.poles.poles[ selectedArray ].spacing * self.scene.road.numPoleFields
        RoadScene.measurementStepWidth =  self.measFieldLength / 10     
        self.numberOfSubimages = 14
        
        #adjust number of subimages if stepwidth is > 5m (according to RP 8 00)
        if( RoadScene.measurementStepWidth > 5 ):
            RoadScene.measurementStepWidth = 5;
            self.numberOfSubimages = int( RoadScene.measFieldLength / RoadScene.measurementStepWidth )
            self.numberOfSubimages = self.numberOfSubimages + 4
            
        RoadScene.measurementStartPosition = - 3 * RoadScene.measurementStepWidth / 2
        
        print '    selected Pole array: ' +  str( selectedArray )
        print '    PoleSpacing: ' + str( self.poles.poles[ selectedArray ].spacing )
        print '    measurementStartPosition: ' + str( RoadScene.measurementStartPosition )
        print '    measurementStepWidth: ' + str( RoadScene.measurementStepWidth ) 
        print '    measFieldLength: ' + str( RoadScene.measFieldLength ) 
        print '    numberOfSubimages: ' + str( self.numberOfSubimages )
        
    ## calculate the horizontal and vertical opening angle of the camera required for the rendering
    def calcOpeningAngle( self ):
        RoadScene.verticalAngle = ( 2 * math.atan( RoadScene.sensorHeight / ( 2 * self.scene.description.focalLength ) ) ) / math.pi * 180
        RoadScene.horizontalAngle = ( 2 * math.atan( RoadScene.sensorWidth / ( 2 * self.scene.description.focalLength ) ) ) / math.pi * 180