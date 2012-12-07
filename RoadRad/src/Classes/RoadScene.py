# This Python file uses the following encoding: utf-8

import sys
import os
import math
import Scene as modulScene
import TargetParameters as modulTargetParameters
import Headlight as modulHeadlight
import LIDC as modulLIDC
import Pole as modulPole

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
    
    # constructor
    def __init__( self, xmlfilePath, xmlfileName ):
        # retrieve working directory info
        self.workingDirPath = xmlfilePath
        self.sceneDecriptor = xmlfileName
        
        # initialize objects from roadscene
        self.scene = modulScene.Scene()
        self.targetParameters = modulTargetParameters.TargetParameters()
        self.headlights = [] # object load in function loadHeadlights
        self.lidcs = []      # object load in function loadLIDCs
        self.poles = []      # object load in function loadPoles
        
        # check xml 
        self.parseWithValidation_xml( 'SceneDescription.dtd' )
        self.calcMeasurementField( )
        self.calcOpeningAngle( )
    
    #Validate a given XML file with a given external DTD with error report
    def parseWithValidation_xml( self, dtd_filename ):
        print 'Begining to validate XML File.'
        print '    xml Filename: ' + str( self.sceneDecriptor )
        print '    dtd Filename: ' + str( dtd_filename )
        
        dtd = etree.DTD( dtd_filename )
        configfile = self.workingDirPath + '/' + self.sceneDecriptor 
        root = etree.parse( configfile )

        if not( dtd.validate( root ) ):
            print( dtd.error_log.filter_from_errors( )[ 0 ] )
            sys.exit( 0 )
        else:
            print 'xml is valid'
            print 'Begining to parse XML Config.'        
            #load scene parameter
            self.loadScene( root )
            print '    scene parameters loaded'
            
            #load target parameter
            self.loadTargetParameter( root )
            print '    target parameters loaded'
            
            #load headlights
            self.loadHeadlights( root )
            print '    headlight parameters loaded'
            
            #load luminous intensity distribution curve
            self.loadLIDCs( root )
            print '    lidc parameters loaded'
            
            #load pole array or single pole
            self.loadPoles( root )
            print '    pole parameters loaded'
        
    def loadScene( self, root ):
        sceneDesc = root.find( 'Scene/Description' )
        self.scene.description.title = sceneDesc.get( 'Title' )
        self.scene.description.environment = sceneDesc.get( 'Environment' )
        self.scene.description.focalLength = float( sceneDesc.get( 'FocalLength' ) )

        roadDesc = root.find( 'Scene/Road' )
        self.scene.road.numLanes = int( roadDesc.get( 'NumLanes' ) )
        self.scene.road.numPoleFields = float( roadDesc.get( 'NumPoleFields' ) )
        self.scene.road.laneWidth = float( roadDesc.get( 'LaneWidth' ) )
        self.scene.road.sidewalkWidth = float( roadDesc.get( 'SidewalkWidth' ) )
        self.scene.road.surface = roadDesc.get( 'Surface' )
        self.scene.road.qZero = float( roadDesc.get( 'qZero' ) )

        #print the q0 factor of pavement surface depend on r-table
        if self.scene.road.surface == 'R1' and self.scene.road.qZero != 0.00:
            self.scene.road.qZero = self.scene.road.qZero / 0.1
        elif self.scene.road.surface == 'R2' and self.scene.road.qZero != 0.00:
            self.scene.road.qZero = self.scene.road.qZero / 0.07
        elif self.scene.road.surface == 'R3' and self.scene.road.qZero != 0.00:
            self.scene.road.qZero = self.scene.road.qZero / 0.07
        elif self.scene.road.surface == 'R4' and self.scene.road.qZero != 0.00:
            self.scene.road.qZero = self.scene.road.qZero / 0.08
        elif self.scene.road.surface == 'C1' and self.scene.road.qZero != 0.00:
            self.scene.road.qZero = self.scene.road.qZero / 0.1
        elif self.scene.road.surface == 'C2' and self.scene.road.qZero != 0.00:
            self.scene.road.qZero = self.scene.road.qZero / 0.07
            
        calcDesc = root.find( 'Scene/Calculation' )
        self.scene.calculation.din13201 = calcDesc.get( 'VeilingLuminance' )
        self.scene.calculation.veilingLuminance = calcDesc.get( 'DIN13201' )
        self.scene.calculation.veilingLuminanceMethod = calcDesc.get( 'VeilingLuminanceMethod' )
        self.scene.calculation.tresholdLuminanceFactor = calcDesc.get( 'TresholdLuminanceFactor' )
           
    def loadTargetParameter( self, root ):
        viewpointDesc = root.find( 'TargetParameters/ViewPoint' )
        self.targetParameters.viewPoint.distance = float( viewpointDesc.get( 'Distance' ) )
        self.targetParameters.viewPoint.height = float( viewpointDesc.get( 'Height' ) )
        self.targetParameters.viewPoint.targetDistanceMode = viewpointDesc.get( 'TargetDistanceMode' )
        self.targetParameters.viewPoint.xOffset = float( viewpointDesc.get( 'XOffset' ) )
        self.targetParameters.viewPoint.viewDirection = viewpointDesc.get( 'ViewDirection' )
        
        targetDesc = root.find( 'TargetParameters/Target' )
        self.targetParameters.target.size = float( targetDesc.get( 'Size' ) )
        self.targetParameters.target.reflectency = float( targetDesc.get( 'Reflectancy' ) )
        self.targetParameters.target.roughness = float( targetDesc.get( 'Roughness' ) )
        self.targetParameters.target.specularity = float( targetDesc.get( 'Specularity' ) )
        self.targetParameters.target.position = targetDesc.get( 'Position' )
        self.targetParameters.target.onLane = int( targetDesc.get( 'OnLane' ) ) - 1

        #check if the scene parameter 'numlane' and 'target lane' make sense
        if( self.scene.road.numLanes - self.targetParameters.target.onLane < 1 ):
            print 'Numlanes and TargetPosition Parameters are impossible'
            sys.exit( 0 )

    def loadLIDCs( self, root ):
        lidcDesc = root.findall( 'LIDCs/LIDC' )
        for lidcEntry in lidcDesc:
            lidc = modulLIDC.LIDC( )
            lidc.name = lidcEntry.get( 'Name' )
            lidc.lightSource = lidcEntry.get( 'LightSource' )
            lidc.lightLossFactor = float( lidcEntry.get( 'LightLossFactor' ) )
            lidc.spRatio = float( lidcEntry.get( 'SPRatio' ) )
            self.lidcs.append( lidc )

    def loadHeadlights( self, root ):
        headlightDesc = root.findall( 'Headlights/Headlight' )
        for headlightEntry in headlightDesc:
            headlight = modulHeadlight.Headlight( )
            headlight.lidc = headlightEntry.get( 'LIDC' ) 
            headlight.headlightDistanceMode = headlightEntry.get( 'HeadlightDistanceMode' ) 
            headlight.distance = float( headlightEntry.get( 'Distance' ) )
            headlight.height = float( headlightEntry.get( 'Height' ) )
            headlight.width = float( headlightEntry.get( 'Width' ) )  
            headlight.slopeAngle = float( headlightEntry.get( 'SlopeAngle' ) )
            headlight.lightDirection = headlightEntry.get( 'LightDirection' ) 
            headlight.onLane = int( headlightEntry.get( 'OnLane' )  ) - 1
            self.headlights.append( headlight )

    def loadPoles( self, root ):
        poleDesc = root.find( 'Poles' )

        for poleEntry in poleDesc:
            print poleEntry.get( 'Height' )
            if( poleEntry.tag == 'PoleSingle' ):
                pole = modulPole.Pole( True )
                pole.positionX = float( poleEntry.get( 'PositionY' ) )

            else:
                pole = modulPole.Pole( False )
                pole.spacing = float( poleEntry.get( 'Spacing' ) )
                isStaggered = poleEntry.get( 'IsStaggered' )
                if isStaggered == 'False':
                    pole.IsStaggered = False
            
            pole.side = poleEntry.get( 'Side' )
            pole.height = float( poleEntry.get( 'Height' ) )
            pole.lidc = poleEntry.get( 'LIDC' )
            pole.overhang = float( poleEntry.get( 'Overhang' ) )

            self.poles.append( pole )
        
    def calcMeasurementField( self ):
        #calculate necessary measures
        selectedArray = -1
        #select the first nonSingle pole
        for index, pole in enumerate( self.poles ):
            if pole.isSingle == False:
                selectedArray = index
                break
                
        if selectedArray == -1:
            print 'No Pole array defined, cannot position the object. terminating'
            sys.exit( 0 )             
            
        #according to DIN EN 13201 / RP 8 00 (max 5 m)
        RoadScene.measFieldLength = self.poles[ selectedArray ].spacing * self.scene.road.numPoleFields
        RoadScene.measurementStepWidth =  self.measFieldLength / 10     
        self.numberOfSubimages = 14
        
        #adjust number of subimages if stepwidth is > 5m (according to RP 8 00)
        if( RoadScene.measurementStepWidth > 5 ):
            RoadScene.measurementStepWidth = 5;
            self.numberOfSubimages = int( RoadScene.measFieldLength / RoadScene.measurementStepWidth )
            self.numberOfSubimages = self.numberOfSubimages + 4
            
        RoadScene.measurementStartPosition = - 3 * RoadScene.measurementStepWidth / 2
        
        print '    selected Pole array: ' +  str( selectedArray )
        print '    PoleSpacing: ' + str( self.poles[ selectedArray ].spacing )
        print '    measurementStartPosition: ' + str( RoadScene.measurementStartPosition )
        print '    measurementStepWidth: ' + str( RoadScene.measurementStepWidth ) 
        print '    measFieldLength: ' + str( RoadScene.measFieldLength ) 
        print '    numberOfSubimages: ' + str( self.numberOfSubimages )
        
    #calculate the horizontal and vertical opening angle of the camera required for the rendering
    def calcOpeningAngle( self ):
        RoadScene.verticalAngle = ( 2 * math.atan( RoadScene.sensorHeight / ( 2 * self.scene.description.focalLength ) ) ) / math.pi * 180
        RoadScene.horizontalAngle = ( 2 * math.atan( RoadScene.sensorWidth / ( 2 * self.scene.description.focalLength ) ) ) / math.pi * 180