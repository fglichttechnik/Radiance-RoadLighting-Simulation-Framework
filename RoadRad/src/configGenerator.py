# This Python file uses the following encoding: utf-8


#This class reads the scenedescription.xml and generates the appropriate rad files for the rendering

import os
import math
import sys
import Classes.RoadScene as modulRoadscene # import RoadScene.py from subfolder Classes

class ConfigGenerator:
    
    radDirSuffix = '/Rads'
    lidcDirSuffix = '/LIDCs'
    rTableDatSuffix = str( os.getcwd( ) ) + '/3rdParty/' 
    
    #constructor
    def __init__( self, path ):
        # retrieve working directory info
        self.xmlConfigPath = path
        self.xmlConfigName = "SceneDescription.xml"
        
        if( self.performFileAndDirChecks( ) ):
            # initialize XML as RoadScene object
            self.roadScene = modulRoadscene.RoadScene( self.xmlConfigPath, self.xmlConfigName )
            self.road = self.roadScene.scene.road
            self.viewPoint = self.roadScene.targetParameters.viewPoint
            self.target = self.roadScene.targetParameters.target
            self.lidcs = self.roadScene.lidcs.lidcs
            self.headlights = self.roadScene.headlights.headlights
            self.poles = self.roadScene.poles.poles
            # do all config Outputs
            self.printRoadRads( )
            self.makeRadfromIES( )
            self.printDashedWhiteRad( )
            self.printPoleConfig( )
            self.printLightsRad( )
            self.printCarlightsRad( )
            #self.printLuminaireRad( )
            self.printNightSky( )
            self.rTableCal( )
            self.printMaterialsRad( )
            self.printRView( )
            self.printTarget( )
            self.printTargets( )
            self.veilCal( )

    #checks the presence of a few important files and directories before begining
    def performFileAndDirChecks( self ):
        print 'Working Directory: ' + str( self.xmlConfigPath )
        print 'Attempting to locate configuration in: ' + str( self.xmlConfigPath ) + '/' + str( self.xmlConfigName )
        
        if( not os.path.isdir( self.xmlConfigPath ) ):
            print 'Scene directory not found in the working directory, Quitting'
            return False
        
        if( not os.path.isfile( self.xmlConfigPath + '/' + self.xmlConfigName ) ):
            print 'No config found, Quitting'
            return False
        
        print 'Found: ' + str( self.xmlConfigName )
        
        if( not os.path.isdir( self.xmlConfigPath + ConfigGenerator.radDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + ConfigGenerator.radDirSuffix )
            print 'Made directory Rads to output the Rad configs.'
        
        return True
    
    #Output the Road config files
    def printRoadRads( self ):
            
        print 'Generating: road.rad'
        print '    sidewalk width: ' + str( self.road.sidewalkWidth )
        print '    sidewalk height: ' + str( self.roadScene.sidewalkHeight )
        print '    number of numlanes: ' + str( self.road.numLanes )
        print '    scene length: ' + str( self.roadScene.sceneLength )
        print '    lane width: ' + str( self.road.laneWidth )
        f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/road.rad', "w" )
    
        f.write( '######road.rad######\npavement polygon pave_surf\n0\n0\n12\n' )
        f.write( "%d -%d %d\n" % ( 0, self.roadScene.sceneLength / 2, 0 ) )
        f.write( "%d -%d %d\n" % ( self.road.numLanes * self.road.laneWidth, self.roadScene.sceneLength / 2, 0 ) )
        f.write( "%d %d %d\n" % ( self.road.numLanes * self.road.laneWidth, self.roadScene.sceneLength / 2, 0 ) )
        f.write( "%d %d %d\n\n" % ( 0, self.roadScene.sceneLength / 2, 0 ) )
        f.write( "!genbox concrete curb1 %d %d %f | xform -e -t -%d -%d 0\n" % ( self.road.sidewalkWidth, self.roadScene.sceneLength, self.roadScene.sidewalkHeight, self.road.sidewalkWidth, self.roadScene.sceneLength / 2 ) )
        f.write( "!genbox concrete curb2 %d %d %f | xform -e -t %d -%d 0\n" % ( self.road.sidewalkWidth, self.roadScene.sceneLength, self.roadScene.sidewalkHeight, self.road.numLanes * self.road.laneWidth, self.roadScene.sceneLength / 2 ) )
        f.write( "!xform -e -t %d -120 .001 -a 40 -t 0 10 0 -a 1 -t %d 0 0 %s/dashed_white.rad\n\n" % ( self.road.laneWidth, self.road.laneWidth, self.xmlConfigPath + ConfigGenerator.radDirSuffix ) )

        f.write( 'grass polygon lawn1\n0\n0\n12\n' )
        f.write( "-%d -%d %f\n" % ( self.road.sidewalkWidth, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
        f.write( "-%d %d %f\n" % ( self.road.sidewalkWidth, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
        f.write( "-%d %d %f\n" % ( 55506, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
        f.write( "-%d -%d %f\n\n\n" % ( 55506, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
    
        f.write( 'grass polygon lawn2\n0\n0\n12\n' )
        f.write( "%d -%d %f\n" % ( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
        f.write( "%d %d %f\n" % ( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
        f.write( "%d %d %f\n" % ( 1140, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
        f.write( "%d -%d %f\n" % ( 1140, self.roadScene.sceneLength / 2, self.roadScene.sidewalkHeight ) )
        
        #Adds concrete boxes to emulate road side buildings
        if self.roadScene.scene.description.environment == 'City':
            print '    building city environment'
            f.write( "!genbox house_concrete building_left 1 40 40 | xform -e -t -%d 0 0 | xform -a 20 -t 0 -50 0\n" % ( self.road.sidewalkWidth + 2 ) )
            f.write( "!genbox house_concrete building_right 1 40 40 | xform -e -t %d 0 0 | xform -a 20 -t 0 -50 0\n" % ( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth + 2 ) )
        
        f.close()
        print '    done ...'
        print ''
    
    #This function attempts to locate all the ies files mentioned in the scene description
    #and convert them to the RAD files necessary for the rendering
    def makeRadfromIES( self ):
        print 'Generating LIDCs from IES data'

        if( not os.path.isdir( self.xmlConfigPath + ConfigGenerator.lidcDirSuffix ) ):
            print "LIDCs directory not found. Terminating."
            sys.exit(0)
        else:
            for lidcArray in self.lidcs:
            
                if( not os.path.isfile( self.xmlConfigPath + ConfigGenerator.lidcDirSuffix + '/' + lidcArray.name + '.ies' ) ):
                    print lidcArray.name + " LIDC not found in the designated LDCs directory. Terminating."
                    sys.exit(0)
                else:
                    iesPath = self.xmlConfigPath + ConfigGenerator.lidcDirSuffix + '/' + lidcArray.name + '.ies'
                    print "    Given light source type " + lidcArray.lightSource
                    print "    Given LIDC name: " + str( lidcArray.name )
                    print "    Given light loss factor: " + str( lidcArray.lightLossFactor )
                    cmd = 'ies2rad -dm -t ' + lidcArray.lightSource + ' -m ' + str( lidcArray.lightLossFactor ) + ' -l ' + self.xmlConfigPath + ConfigGenerator.lidcDirSuffix + ' ' + iesPath  
                    #-dm for meters
                    #-t for lightsource type in lamp.tab (radiance dir)
                    #-l library dir prefix for pathes in generated .rad file?
                    #-m for an output factor -- light loss factor
                    #cmd = 'ies2Rad -t ' + entry.lightSource + ' ' + iesPath
                    print '    ies2rad lights command: ' + str( cmd )
                    os.system( cmd )
                    
                    radpath_old = iesPath.replace( '.ies', '.rad' )
                    radpath_new = iesPath.replace( '.ies', '.txt' )
                    print '    ' + str( radpath_old )
                    print '    ' + str( radpath_new )
                    os.rename(radpath_old, radpath_new )
                    
                    datfile_old = open( radpath_new, 'r' )
                    datfile_new = open( radpath_old, 'w' )
                    
                    for line in datfile_old.readlines():
                        if line.find( lidcArray.name + '.dat' ) == -1:
                            datfile_new.write( line )
                        else:
                            datfile_new.write( line.replace( lidcArray.name + '.dat', radpath_old.replace( '.rad', '.dat' ) ) )
                            
                    print '    done ...'
                    print ''
                    
    #White paint line that divides the lanes
    def printDashedWhiteRad( self ):
            print 'Generating: dashed_white.rad'
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/dashed_white.rad', "w" )
            f.write( "######dashed_white.rad######\n" )
            f.write( "white_paint polygon lane_dash\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "12\n" )
            f.write( str( -self.roadScene.markingWidth / 2) + " 0 0.01\n")
            f.write( str( self.roadScene.markingWidth / 2 ) + " 0 0.01\n")
            f.write( str( self.roadScene.markingWidth / 2 ) + " " + str( self.roadScene.markingLength ) + " 0.01\n")
            f.write( str( -self.roadScene.markingWidth / 2 ) + " " + str( self.roadScene.markingLength ) + " 0.01\n")
            f.close()
            
            print '    done ...'
            print ''
    
    #Basic geometry of the pole is defined here and named on the basis of the LDC's of the light sources that
    #they are holding
    def printPoleConfig( self ):
            print 'Generating: Light Pole Rad files'
            print self.poles
            for index, poleArray in enumerate( self.poles ):
                if poleArray.isSingle:
                    print '    build single pole number: ' + str( index ) + ' with ' + str( poleArray.lidc )
                else:
                    print '    build array pole number: ' + str( index ) + ' with ' + str( poleArray.lidc )
                
                f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/' + poleArray.lidc + '_' + str( index )  + '_light_pole.rad', "w" )
                f.write( "######light_pole.rad######\n" )
                f.write( "!xform -rz " + str( self.roadScene.lidcRotation ) + " -t " + str( poleArray.overhang ) + " 0 " + str( poleArray.height - self.roadScene.poleRadius ) + " " + str( self.xmlConfigPath + ConfigGenerator.lidcDirSuffix ) + "/" + str( poleArray.lidc ) + ".rad\n\n" )
                #f.write( "chrome cylinder pole\n" )
                #f.write( "0\n" )
                #f.write( "0\n" )
                #f.write( "7\n" )
                #f.write( "0 0 0\n" )
                #f.write( "0 0 " + str( poleArray.height ) + "\n" )
                #f.write( str( self.roadScene.poleRadius ) + "\n\n")
                #f.write( "chrome cylinder mount\n" )
                #f.write( "0\n" )
                #f.write( "0\n" )
                #f.write( "7\n" )
                #f.write( "0 0 " + str( poleArray.height ) + "\n" )
                #f.write( str( poleArray.overhang - self.roadScene.poleRadius  ) + " 0 " + str( poleArray.height ) + "\n" )
                #f.write( str( self.roadScene.poleRadius ) )
                f.close( )
            
            print '    done ...'
            print ''
    
    #This function places the various poles in the scene
    def printLightsRad( self ):
            print 'Generating: light_s.rad'
            firstArrayHandled = False
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/lights_s.rad', "w" )
            f.write( "######lights_s.rad######\n" )
            for index, poleArray in enumerate( self.poles ):
                if poleArray.isSingle == True:
                    if poleArray.side == "Left":
                        f.write( "!xform -t -" + str( self.road.sidewalkWidth ) + " " + str( poleArray.positionY ) + " 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/" + poleArray.lidc + "_" + str(index)  + "_light_pole.rad\n" )
                    else:
                        f.write( "!xform -rz -180 -t "+ str( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth )+" " + str( poleArray.positionY ) + " 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/" + poleArray.lidc + "_" + str(index) + "_light_pole.rad\n" )
                elif poleArray.side == "Left":
                    print "    making left poles"
                    if firstArrayHandled == False or poleArray.isStaggered == False:
                        f.write( "!xform  -t -" + str( self.road.sidewalkWidth ) + " -" + str( self.roadScene.numberOfLightsBeforeMeasurementArea * poleArray.spacing ) +" 0 -a " + str( self.roadScene.numberOfLightsPerArray ) + " -t 0 "+ str( poleArray.spacing ) +" 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/" + poleArray.lidc + '_' + str( index )  + "_light_pole.rad\n" )
                        firstArrayHandled = True
                    else:
                        f.write( "!xform -t -" + str( self.road.sidewalkWidth ) + " -" + str( self.roadScene.numberOfLightsBeforeMeasurementArea * 0.5 * poleArray.spacing ) +" 0 -a " + str( self.roadScene.numberOfLightsPerArray ) + " -t 0 "+ str( poleArray.spacing ) +" 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/" + poleArray.lidc + '_' + str( index )  + "_light_pole.rad\n" )
                else:
                    print "    making right poles"
                    if firstArrayHandled == False or poleArray.isStaggered == False:
                        f.write( "!xform -rz -180 -t " + str( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth ) + " -"+ str( self.roadScene.numberOfLightsBeforeMeasurementArea * poleArray.spacing ) +" 0 -a " + str( self.roadScene.numberOfLightsPerArray ) + " -t 0 "+ str( poleArray.spacing ) +" 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/" + poleArray.lidc + '_' + str( index )  + "_light_pole.rad\n" )
                        firstArrayHandled = True
                    else:
                        f.write( "!xform -rz -180 -t " + str( self.road.numLanes * self.road.laneWidth + self.road.sidewalkWidth ) + " -"+ str( self.roadScene.numberOfLightsBeforeMeasurementArea * 0.5 * poleArray.spacing ) +" 0 -a " + str( self.roadScene.numberOfLightsPerArray ) + " -t 0 "+ str( poleArray.spacing ) +" 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/" + poleArray.lidc + '_' + str( index )  + "_light_pole.rad\n" )
            f.close( )
            
            print '    done ...'
            print ''
    
    # print Headlights from Car 
    def printCarlightsRad( self ):
            print 'Generating: headlight.rad'
            if self.headlights.__len__() > 0:
                f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/headlight.rad', "w" )
                f.write( "######headlight.rad######\n" )
                for index, headlightArray in enumerate( self.headlights ):
                    print '    Generating: Carlight number: ' + str( index ) + ' with ' + str( headlightArray.lidc )
                    print '    Car on Lane: ' + str( headlightArray.onLane + 1 )
                    print '    Headlight Height: ' + str( headlightArray.height )
                    print '    Headlight Width: ' + str( headlightArray.width )
                    print '    Headlight Distance: ' + str( headlightArray.distance )
                    print '    Angle of Slope: ' + str( headlightArray.slopeAngle )
                    print '    Headlight Distance Mode: ' + str( headlightArray.headlightDistanceMode )
                    #f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/' + str( index ) + '_headlight.rad', "w" )
                    if headlightArray.lightDirection == 'opposite':
                        print '    light direction: opposite'
                        f.write( "!xform -n oppositeH_" + str( index ) + " -rx -" + str( 90.0 - headlightArray.slopeAngle ) + " -t " + str( self.road.laneWidth * ( headlightArray.onLane + 0.5 ) - ( headlightArray.width / 2 ) ) + " " + str( headlightArray.distance + self.roadScene.measFieldLength ) + " " + str( headlightArray.height ) + " -a 2 -t " + str( headlightArray.width ) + " 0 0 " + self.xmlConfigPath + ConfigGenerator.lidcDirSuffix + "/" + headlightArray.lidc + ".rad\n" )
                    else:
                        print '    light direction: same'
                        f.write( "!xform -n sameH_" + str( index ) + " -rx " + str( 90.0 - headlightArray.slopeAngle ) + " -t " + str( self.road.laneWidth * ( headlightArray.onLane + 0.5 ) - ( headlightArray.width / 2 ) ) + " -" + str( headlightArray.distance ) + " " + str( headlightArray.height ) + " -a 2 -t " + str( headlightArray.width ) + " 0 0 " + self.xmlConfigPath + ConfigGenerator.lidcDirSuffix + "/" + headlightArray.lidc + ".rad\n" )
                f.close( )
            else:
                print '    no headlights are given in the xml'
                
            print '    done ...'
            print ''
    
    # def printLuminaireRad( self ):
#             print 'Generating: LDC Rad files'
#             
#             for entry in self.lights:
#                 f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/' + entry.name + '.rad', "w" )
#                 f.write( "void brightdata ex2_dist\n" )
#                 f.write( "6 corr " + self.xmlConfigPath + "/LDCs/" + entry.name + ".dat" + " source.cal src_phi2 src_theta -my\n" )
#                 f.write( "0\n" )
#                 f.write( "1 1\n" )
#                 f.write( "ex2_dist light ex2_light\n\n" )
#                 f.write( "0\n" )
#                 f.write( "0\n" )
#                 f.write( "3 2.492 2.492 2.492\n\n" )    #TODO: this shall be taken from original file
#                 f.write( "ex2_light sphere ex2.s\n" )
#                 f.write( "0\n" )
#                 f.write( "0\n" )
#                 f.write( "4 0 0 0 0.5\n" )
#                 f.close( )
    
    #Night sky Rad file
    def printNightSky( self ):
            print 'Generating: night_sky.rad'
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/night_sky.rad', "w" )
            f.write( "######night_sky.rad######\n" )
            f.write( "void brightfunc skyfunc\n" )
            f.write( "2 skybr skybright.cal\n" )
            f.write( "0\n" )
            f.write( "7 -1 11.620399 8.936111 1.637813 0.033302 -0.250539 0.967533\n\n" )
            f.write( "skyfunc glow ground_glow\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 1e-5 8e-6 5e-6 0\n\n" )
            #here for ref image
            #f.write( "4 1 1 1 0\n\n" )
            f.write( "ground_glow source ground\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 0 0 -1 180\n\n" )
            f.write( "skyfunc glow sky_glow\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 2e-6 2e-6 1e-5  0\n\n" )
            #here for ref image
            #f.write( "4 0 0 0  0\n\n" )
            f.write( "sky_glow source sky\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 0 0 1 180\n" )
            f.close( )
            
            print '    done ...'
            print ''
    
    #All the materials used in the simulation are defined here
    def printMaterialsRad( self ):
            print 'Generating: materials.rad'
            print '    surface type is ' + self.road.surface + ' with a qZero of ' + str( self.road.qZero )
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/materials.rad', "w" )
            f.write( "######materials.rad######\n" )
            
            #road surface with Light Loss Factor (LLF)
            #the accumulation of dirt on luminaires results in a loss in light output on the roadway LDD RP 8 00
            #surfaces: R1-R4, BRDF 1-4.5°, plastic (100 diffus), C1, C2 C2W3 C2W4
            
            rTableCal = str( self.xmlConfigPath + ConfigGenerator.radDirSuffix ) + '/r-table.cal'

            if self.road.surface == 'plastic':            
                f.write( "void plastic pavement\n" )
                f.write( "0\n" )
                f.write( "0\n" )
                f.write( "5 0.14 0.14 0.14 0 0 \n\n" )
                
            elif self.road.surface == 'plastic_improvedPhilips':            
                f.write( "void plastic pavement\n" )
                f.write( "0\n" )
                f.write( "0\n" )
                f.write( "5 0.14 0.14 0.14 0.03 0.01 \n\n" )
                
            elif self.road.surface == 'R4':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "R4/r4-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
            
            elif self.road.surface == 'R3':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "R3/r3-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
                
            elif self.road.surface == 'R2':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "R2/r2-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
                
            elif self.road.surface == 'R1':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "R1/r1-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
                
            elif self.road.surface == 'C1':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "C1/c1-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
            
            elif self.road.surface == 'C2':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "C2/c2-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
            
            elif self.road.surface == 'C2W3':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "C2W3/c2w3-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
            
            elif self.road.surface == 'C2W4':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "C2W4/c2w4-table.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )
            
            elif self.road.surface == 'BRDF1345':
                f.write( "void plasdata pavement\n" )
                f.write( "6 refl " + str( ConfigGenerator.rTableDatSuffix ) + "BRDF/brdf.dat " + str( rTableCal ) + " alfa gamma beta\n" )
                f.write( "0\n" )
                f.write( "4 1 1 1 1 \n\n" )

            else:
                print 'no valid surfacetype given (R1-R4, BRDF1345, C1, C2 C2W3 C2W4 or plastic, plastic_improvedPhilips)'
                sys.exit( 0 )
            
            #sidewalk
            f.write( "void plastic concrete\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "5 .14 .14 .14 0 0\n\n" )
            
            #houses
            f.write( "void plastic house_concrete\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "5 .14 .14 .14 0 0\n\n" )
            # dash yellow
            f.write( "void plastic yellow_paint\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "5 .7 .7 .01 0 0\n\n" )
            # dash white
            f.write( "void plastic white_paint\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "5 .7 .7 .7 0 0\n\n" )
            # grass
            f.write( "void plastic grass\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "5 0 .1 .02 0 0\n\n" )
            # target material
            print '    target reflectancy: ' + str( self.target.reflectency )
            print '    target specularity: ' + str( self.target.specularity )
            print '    target roughness: ' + str( self.target.roughness )
            
            f.write( "void plastic targetMaterial\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( '5 {0} {0} {0} '.format( self.target.reflectency ) + str( self.target.specularity ) +" "+ str( self.target.roughness ) + " \n\n" )
            # pole cylinder
            f.write( "void metal chrome\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "5 .2 .2 .2 .05 .05\n\n" )
            # glow box
            f.write( "void glow self_box\n" )
            f.write( "0\n" )
            f.write( "0\n" )
            f.write( "4 1 1 1 0\n\n" )
            f.close( )
            
            print '    done ...'
            print ''
    
    #Prints view point files.
    #Based on the viewpoint mode, one of several viewpoints are written
    def printRView( self ):

        print 'Generating: eye.vp'
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
            viewDirection = "0 0.999847 -0.017467 " 
        
        #add x-offset point of view
        print '    viewpoint x-offset: ' + str( self.viewPoint.xOffset ) 
        print '    viewpoint view direction: ' + str( viewDirection ) 
        print '    viewpoint height: ' + str( self.viewPoint.height ) 
        print '    viewpoint distance: ' + str( self.viewPoint.distance ) 
        
        if self.viewPoint.targetDistanceMode == 'fixedViewPoint':
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/eye.vp', "w" )
            f.write( "######eye.vp######\n")            
            f.write( "rview -vtv -vp " + str( ( self.road.laneWidth * ( self.target.onLane + 0.5 ) ) + self.viewPoint.xOffset ) +" -" + str( self.viewPoint.distance ) + " " + str( self.viewPoint.height ) + " -vd " + viewDirection + " -vh " + str( self.roadScene.verticalAngle ) + " -vv " + str( self.roadScene.horizontalAngle ) + "\n" )
            f.close( )
        else:
            for i in range( self.numberOfSubimages  ):
                f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/eye' + str( i ) + '.vp', "w" )
                f.write( "######eye.vp######\n")
                f.write( "rview -vtv -vp " + str( ( self.road.laneWidth * ( self.target.onLane + 0.5 ) ) + self.viewPoint.xOffset ) + " " + str( ( -1 * self.viewPoint.distance ) + i * self.roadScene.measurementStepWidth ) + " " + str( self.viewPoint.height ) + " -vd " + viewDirection + " -vh " + str( self.roadScene.verticalAngle ) + " -vv " + str( self.roadScene.horizontalAngle ) + "\n" )
                f.close( )
                
        #print view point files for plan view of the roadway
        #view down on the roadway
        f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/eye_down.vp', "w" )
        f.write( "######eye.vp######\n" )
        #f.write( "rview -vtv -vp " + str( self.road.laneWidth ) + " 0 60 -vd 0 0 -1 -vu -1 0 0 -vh 100 -vv 20\n" )
        f.write( "rview -vtl -vp " + str( self.road.laneWidth ) + " 1 60 -vd 0 0 -1 -vu -1 0 0 -vh 100 -vv 20 -vs 0 -vl 0\n" )

        f.close( )
        #view up from the roadway
        f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/eye_up.vp', "w" )
        f.write( "######eye.vp######\n" )
        f.write( "rview -vtv -vp " + str( self.road.laneWidth ) + " 0 0 -vd 0 0 1 -vu 0 -1 0 -vh 100 -vv 100\n" )
        f.close( )
        
        print '    done ...'
        print ''
    
    #Definition of the geometry of the target.
    def printTarget( self ):
            print 'Generating: target.rad'
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/target.rad', "w" )
            f.write( "######target.rad######\n")
            f.write( '!genbox targetMaterial stv_target {0} 0.05 {0}\n'.format( self.target.size ) )
            f.close( )
            
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/self_target.rad', "w" )
            f.write( "######target.rad######\n")
            f.write( '!genbox self_box stv_target {0} 0.05 {0}\n'.format( self.target.size ) )
            f.close( )
    
    #Several files are written here to place the targets at different locations in the scene.
    #each files is then ran as a separate simulation.
    #Placement of the targets is done relative to the first pole array defined in the scene description
    #10 targets between the two consecutive poles, and 2 before the first and after the last each.
    def printTargets( self ):
            
            dist = self.roadScene.measurementStartPosition            
            targetXPos = self.road.laneWidth
                
            if self.target.position == "Center":
                targetXPos = targetXPos * (self.target.onLane + 0.5 )
            elif self.target.position == "Left":
                targetXPos = targetXPos * (self.target.onLane + 0.25 )
            elif self.target.position == "Right":
                targetXPos = targetXPos * (self.target.onLane + 0.75 )
            else:
                print "unrecognized Target Position " + self.scene.position
                print "possible values: Center, Left, Right"
                print "WILL EXIT"
                sys.exit(0)
                
            targetfile = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/targetdistances.txt', "w" )
            for i in range( self.roadScene.numberOfSubimages  ):
                targetfile.write( str(dist) + '\n')
                print 'Generating: target_' + str( i ) + '.rad'
                f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/target_' + str( i ) + '.rad', "w" )
                f.write( "######target_0.rad######\n")
                f.write( "!xform -e -t " + str( targetXPos ) + " " + str( dist ) + " 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/target.rad\n" )
                f.close( )
                dist = dist + self.roadScene.measurementStepWidth
            targetfile.close( )
            
            dist = self.roadScene.measurementStartPosition
            for i in range( self.roadScene.numberOfSubimages  ):
                print 'Generating: self_target_' + str( i ) + '.rad'
                f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/self_target_' + str( i ) + '.rad', "w" )
                f.write( "######target_0.rad######\n")
                f.write( "!xform -e -t " + str( targetXPos ) + " " + str( dist ) + " 0 " + self.xmlConfigPath + ConfigGenerator.radDirSuffix + "/self_target.rad\n" )
                f.close( )
                dist = dist + self.roadScene.measurementStepWidth
                
            print '    done ...'
            print ''
                
    def veilCal( self ):
        if self.roadScene.scene.calculation.veilingLuminance == 'on':
            print 'Generating veil.cal'
            f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/veil.cal', "w" )
            f.write( 'PI : 3.14159265358979323846;\n' )
            f.write( 'bound(a,x,b) : if(a-x,a,if(x-b,b,x));\n' )
            f.write( 'Acos(x) : acos(bound(-1, x, 1));\n\n' )
            f.write( 'mul(t) : if(.5*PI/180-t, 9.2/.5^2, 9.2/(180/PI)^2/(t*t));\n\n' )
            f.write( 'Dx1 = Dx(1); Dy1 = Dy(1); Dz1 = Dz(1); {minor optimization}\n\n' )
            f.write( 'angle(i) = Acos(SDx(i)*Dx1+SDy(i)*Dy1+SDz(i)*Dz1);\n\n' )
            f.write( 'sum(i) = if(i-.5, mul(angle(i))*I(i)+sum(i-1), 0);\n\n' )
            f.write( 'veil = le(1)/179 * sum(N);\n\n' )
            
            f.write( 'ro = ri(1) + veil;\n' )
            f.write( 'go = gi(1) + veil;\n' )
            f.write( 'bo = bi(1) + veil;\n' )
            
            f.write( 'V(i) : select(i, veil);\n' )
            f.write( 'Lv = V(0);\n' )
            f.close( )
            print '    done ...'
            print ''
    
    def rTableCal( self ):
            if not self.road.surface == 'plastic':
                print 'Generating r-table.cal'
                f = open( self.xmlConfigPath + ConfigGenerator.radDirSuffix + '/r-table.cal', "w" )
                f.write( 'PI : 3.14159265358979323846;\n' )
                f.write( 'alfa(x,y,z) = (180/PI)*Asin(-Dx*Nx-Dy*Ny-Dz*Nz);\n\n' )
                f.write( 'gamma(x,y,z) = (180/PI)*Acos(x*Nx + y*Ny + z*Nz);\n\n' )
                f.write( 'beta(x,y,z) = if(sqrt(x^2+y^2),(180/PI)*Acos((x/sqrt(x^2+y^2))*(Dx/sqrt(Dx^2+Dy^2))+(y/sqrt(x^2+y^2))*(Dy/sqrt(Dx^2+Dy^2))),0);\n\n' )
                if self.road.qZero > 0: 
                    f.write( 'refl(v,x,y,z) = if((x*Nx + y*Ny + z*Nz),v*' + str( self.road.qZero ) + '/(10000*(x*Nx + y*Ny + z*Nz)^3),0);\n' )
                else:
                    f.write( 'refl(v,x,y,z) = if((x*Nx + y*Ny + z*Nz),v/(10000*(x*Nx + y*Ny + z*Nz)^3),0);\n' )
                f.close( )
                
                print '    done ...'
                print ''