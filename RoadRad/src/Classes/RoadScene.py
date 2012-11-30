# This Python file uses the following encoding: utf-8

import sys
import os
import math
import Scene as modulScene
import TargetParameters as modulTargetParameters
import Headlight as modulHeadlight
import LIDC as modulLIDC
import Pole as modulPole

from xml.dom.minidom import parse
from helper.xmlproc import xmlproc
from helper.xmlproc import xmlval
from helper.xmlproc import xmldtd

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
        self.validate_xml( xmlfileName, "SceneDescription.dtd" )
        self.parseConfig( )
        self.calcMeasurementField( )
        self.calcOpeningAngle( )
    
    #Validate a given XML file with a given external DTD with error report
    def validate_xml( self, xml_filename, dtd_filename ):
        print "    xml Filename: " + str( xml_filename )
        print "    dtd Filename: " + str( dtd_filename )
        dtd = xmldtd.load_dtd( dtd_filename )
        parser = xmlproc.XMLProcessor( )
        parser.set_application( xmlval.ValidatingApp( dtd, parser ) )
        parser.dtd = dtd
        parser.ent = dtd
        parser.parse_resource( xml_filename )

        if __name__ == "__main__":
            xml_filename, dtd_filename = sys.argv[1], sys.argv[2]
            validate_xml( xml_filename, dtd_filename )
        print "xml is valid"
            
    def parseConfig( self ):
    #Parse XML data from given XML file 
        
        print 'Begining to parse XML Config.'
        configfile = open( self.workingDirPath + '/' + self.sceneDecriptor, 'r' )
        root = parse( configfile )
        configfile.close( )
        
        #load scene parameter
        self.loadScene( root )
        print "scene parameters loaded"
        
        #load target parameter
        self.loadTargetParameter( root )
        print "target parameters loaded"
        
        #load headlights
        self.loadHeadlights( root )
        print "headlight parameters loaded"
        
        #load luminous intensity distribution curve
        self.loadLIDCs( root )
        print "lidc parameters loaded"
        
        #load pole array or single pole
        self.loadPoles( root )
        print "pole parameters loaded"
        
    def loadScene( self, root ):
        sceneDesc = root.getElementsByTagName( 'Description' )
        if( sceneDesc[0].attributes ):
            self.scene.description.title = sceneDesc[0].attributes["Title"].value
            self.scene.description.environment = sceneDesc[0].attributes["Environment"].value
            self.scene.description.focalLength = float( sceneDesc[0].attributes["FocalLength"].value )
    
        roadDesc = root.getElementsByTagName( 'Road' )
        if( roadDesc[0].attributes ):
            self.scene.road.numLanes = int( roadDesc[0].attributes["NumLanes"].value )
            self.scene.road.numPoleFields = float( roadDesc[0].attributes["NumPoleFields"].value )
            self.scene.road.laneWidth = float( roadDesc[0].attributes["LaneWidth"].value )
            self.scene.road.sidewalkWidth = float( roadDesc[0].attributes["SidewalkWidth"].value )
            self.scene.road.surface = roadDesc[0].attributes["Surface"].value
            self.scene.road.qZero = float( roadDesc[0].attributes["qZero"].value )

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
            
        calcDesc = root.getElementsByTagName( 'Calculation' )
        if( calcDesc[0].attributes):
            self.scene.calculation.din13201 = calcDesc[0].attributes["VeilingLuminance"].value
            self.scene.calculation.veilingLuminance = calcDesc[0].attributes["DIN13201"].value
            self.scene.calculation.veilingLuminanceMethod = calcDesc[0].attributes["VeilingLuminanceMethod"].value
            self.scene.calculation.tresholdLuminanceFactor = calcDesc[0].attributes["TresholdLuminanceFactor"].value
               
    def loadTargetParameter( self, root ):
        viewpointDesc = root.getElementsByTagName( 'ViewPoint' )
        if( viewpointDesc[0].attributes ):
            self.targetParameters.viewPoint.distance = float( viewpointDesc[0].attributes["Distance"].value )
            self.targetParameters.viewPoint.height = float( viewpointDesc[0].attributes["Height"].value )
            self.targetParameters.viewPoint.targetDistanceMode = viewpointDesc[0].attributes["TargetDistanceMode"].value
            self.targetParameters.viewPoint.xOffset = float( viewpointDesc[0].attributes["XOffset"].value )
            self.targetParameters.viewPoint.viewDirection = viewpointDesc[0].attributes["ViewDirection"].value
        
        targetDesc = root.getElementsByTagName( 'Target' )
        if( targetDesc[0].attributes ):
            self.targetParameters.target.size = float( targetDesc[0].attributes["Size"].value )
            self.targetParameters.target.reflectency = float( targetDesc[0].attributes["Reflectancy"].value )
            self.targetParameters.target.roughness = float( targetDesc[0].attributes["Roughness"].value )
            self.targetParameters.target.specularity = float( targetDesc[0].attributes["Specularity"].value )
            self.targetParameters.target.position = targetDesc[0].attributes["Position"].value
            self.targetParameters.target.onLane = int( targetDesc[0].attributes["OnLane"].value ) - 1

        #check if the scene parameter "numlane" and "target lane" make sense
        if( self.scene.road.numLanes - self.targetParameters.target.onLane < 1 ):
            print "Numlanes and TargetPosition Parameters are impossible"
            sys.exit( 0 )
            
    def loadHeadlights( self, root ):
        headlightDesc = root.getElementsByTagName( 'Headlight' )
        for headlightEntry in headlightDesc:
            if( headlightEntry.attributes ):
                headlight = modulHeadlight.Headlight( )
                headlight.lidc = headlightEntry.attributes["LIDC"].value 
                headlight.headlightDistanceMode = headlightEntry.attributes["HeadlightDistanceMode"].value 
                headlight.distance = float( headlightEntry.attributes["Distance"].value )
                headlight.height = float( headlightEntry.attributes["Height"].value )
                headlight.width = float( headlightEntry.attributes["Width"].value )  
                headlight.slopeAngle = float( headlightEntry.attributes["SlopeAngle"].value )
                headlight.lightDirection = headlightEntry.attributes["LightDirection"].value 
                headlight.onLane = int( headlightEntry.attributes["OnLane"].value  ) - 1
                self.headlights.append( headlight )

    def loadLIDCs( self, root ):
        lidcDesc = root.getElementsByTagName( 'LIDC' )
        for lidcEntry in lidcDesc:
            if( lidcEntry.attributes ):
                lidc = modulLIDC.LIDC( )
                lidc.name = lidcEntry.attributes["Name"].value
                lidc.lightSource = lidcEntry.attributes["LightSource"].value
                lidc.lightLossFactor = float( lidcEntry.attributes["LightLossFactor"].value )
                lidc.spRatio = float( lidcEntry.attributes["SPRatio"].value )
                self.lidcs.append( lidc )

    def loadPoles( self, root ):
        poleDesc = root.getElementsByTagName( 'Poles' )
        for poleEntry in poleDesc[0].childNodes:
            if( poleEntry.attributes ):
                if( poleEntry.nodeName == "PoleSingle" ):
                    pole = modulPole.Pole( True )
                    pole.positionX = float( poleEntry.attributes["PositionY"].value )
                else:
                    pole = modulPole.Pole( False )
                    pole.spacing = float( poleEntry.attributes["Spacing"].value )
                    isStaggered = poleEntry.attributes["IsStaggered"].value
                    if isStaggered == "False":
                        pole.IsStaggered = False

                pole.side = poleEntry.attributes["Side"].value
                pole.height = float( poleEntry.attributes["Height"].value )
                pole.lidc = poleEntry.attributes["LIDC"].value
                pole.overhang = float( poleEntry.attributes["Overhang"].value )
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
            print "No Pole array defined, cannot position the object. terminating"
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
        
        print "    selected Pole array: " +  str( selectedArray )
        print "    PoleSpacing: " + str( self.poles[ selectedArray ].spacing )
        print "    measurementStartPosition: " + str( RoadScene.measurementStartPosition )
        print "    measurementStepWidth: " + str( RoadScene.measurementStepWidth ) 
        print "    measFieldLength: " + str( RoadScene.measFieldLength ) 
        print "    numberOfSubimages: " + str( self.numberOfSubimages )
        
    #calculate the horizontal and vertical opening angle of the camera required for the rendering
    def calcOpeningAngle( self ):
        RoadScene.verticalAngle = ( 2 * math.atan( RoadScene.sensorHeight / ( 2 * self.scene.description.focalLength ) ) ) / math.pi * 180
        RoadScene.horizontalAngle = ( 2 * math.atan( RoadScene.sensorWidth / ( 2 * self.scene.description.focalLength ) ) ) / math.pi * 180