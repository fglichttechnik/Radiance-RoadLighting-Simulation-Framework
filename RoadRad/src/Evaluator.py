#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
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
import Classes.ThresholdIncrement as modulThresholdIncrement
import Classes.Luminances as modulLuminances
import Classes.Illuminances as modulIlluminances
import pdb


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

    #values for calculations
    meanLuminance = 0.0
    uniformityOfLuminance = 0.0
    lengthwiseUniformityOfLuminance = 0.0
    meanIlluminance = 0.0
    minIlluminance = 0.0
    uniformityOfIlluminance = 0.0
    tiSL = 0.0
    tiFixed = 0.0
    tiVar = 0.0
    L_v_SL = 0.0
    L_v_fixed = 0.0
    L_v_var = 0.0
    
    def __init__( self, path ):
        
        # retrieve working directory info
        self.xmlConfigPath = path
        self.xmlConfigName = "SceneDescription.xml"
        # initialize XML as RoadScene object
        self.roadScene = modulRoadscene.RoadScene( self.xmlConfigPath, self.xmlConfigName )

        self.makeOct( )
        self.makePic( )
        self.makeFalsecolor( )
        
        # get parameter for evaluation
        self.Luminances = modulLuminances.Luminances( self.roadScene, self.xmlConfigPath )
        self.Illuminances = modulIlluminances.Illuminances( self.roadScene, self.xmlConfigPath )
        self.TI = modulThresholdIncrement.ThresholdIncrement( self.roadScene, self.xmlConfigPath )
        
        self.evalLuminance( )
        self.evalIlluminance( )
        self.evalSideIlluminance( )
        
        # mode = RP800 or DIN13201
        self.veilingLuminanceForMode( self.roadScene.scene.calculation.veilingLuminanceMethod )
        self.evalVeilingLuminance( self.roadScene.scene.calculation.veilingLuminanceMethod, self.roadScene.scene.calculation.headlightOption )

        #self.filterLightArray( "RP800", "withTarget" )
        #self.filterLightArray( "DIN13201", "fixed" )
        #self.filterLightArray( "DIN13201", "off" )
        
        self.evalThresholdIncrement( self.roadScene.scene.calculation.veilingLuminanceMethod )
        
        self.makeXML( )
        self.checkStandards( )

    # in this function you can make the evaluator as standalone python script, with generating the .oct files with oconv operator
    # but the needed oct. files and generated pics are also made in the simulator!!! these are the oct's with no target!!!
    # so if you wish to make it standalone, copy the makeOct( self ) function from simulator.py
    def makeOct( self ):
        if( os.path.isfile( str( self.xmlConfigPath ) + str ( Evaluator.octDirSuffix ) + '/scene.oct' ) ):
            print '.oct file is existing: scene.oct'
        else:
            print 'there is a problem with the .oct file, its not simulated with simulator --> it not exist!!!'

    def makePic( self ):
        if( not os.path.isdir( self.xmlConfigPath + Evaluator.picDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Evaluator.picDirSuffix )
        if( not os.path.isdir( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix )              
        
        #make pic without target for later evaluation
        print 'make out_radiance.hdr'
        if self.roadScene.targetParameters.viewPoint.targetDistanceMode == 'fixedViewPoint':
            cmd1 = 'rpict -vtv -vf {2}/eye.vp -x {3} -y {4} {0}/scene.oct > {1}/out_radiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
            os.system( cmd1 )
        else:
            cmd1 = 'rpict -vtv -vf {2}/eye0.vp -x {3} -y {4} {0}/scene0.oct > {1}/out_radiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
            os.system( cmd1 )
        print 'make out_irradiance.hdr'
        if self.roadScene.targetParameters.viewPoint.targetDistanceMode == 'fixedViewPoint':
            cmd2 = 'rpict -i -vtv -vf {2}/eye.vp -x {3} -y {4} {0}/scene.oct > {1}/out_irradiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
            os.system( cmd2 )
        else:
            cmd2 = 'rpict -i -vtv -vf {2}/eye0.vp -x {3} -y {4} {0}/scene.oct > {1}/out_irradiance.hdr '.format( self.xmlConfigPath + Evaluator.octDirSuffix , self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix, self.xmlConfigPath + Evaluator.radDirSuffix, Evaluator.horizontalRes, Evaluator.verticalRes )
            os.system( cmd2 )
            
    def makeFalsecolor( self ):
        print 'falsecolor_luminance.hdr'
        cmd0 = 'falsecolor -i {0}/out_radiance.hdr -log 5 -l cd/m^2 > {0}/falsecolor_luminance.hdr'.format( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix )
        os.system( cmd0 )
        print 'falsecolor_illuminance.hdr'
        cmd1 = 'falsecolor -i {0}/out_irradiance.hdr -log 5 -l lx > {0}/falsecolor_illuminance.hdr'.format( self.xmlConfigPath + Evaluator.picDirSuffix + Evaluator.picSubDirSuffix )
        os.system( cmd1 )
        
        print '    done ...'
        print ''
            
    def evalLuminance( self ):
        print 'Evaluate luminances...'
        
        if( not os.path.isdir( self.xmlConfigPath + Evaluator.evalDirSuffix ) ):
                os.mkdir( self.xmlConfigPath + Evaluator.evalDirSuffix )
        
        lumFid = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/Evaluation_Luminance', 'w+' )
        
        L_m_ = []
        L_min_ = []
        U_0_ = []
        U_l_ = []
        
        for laneInOneDirection in range( self.roadScene.scene.road.numLanes ):
            print '    Viewer on lane number: ' + str( laneInOneDirection )
            lumFid.write('    Viewer on lane number: ' + str( laneInOneDirection ) + '\n' )
            
            L_m = 0
            L_min__ = []
            L_l_min_ = []
            L_l_m_ = []
            
            for lane in range( self.roadScene.scene.road.numLanes ):
                print '    lane: ' + str( lane )
                lumFid.write('    lane: ' + str( lane ) + '\n')
                evalLumDir = self.xmlConfigPath + Evaluator.evalDirSuffix + '/luminances.txt'
                lumFile = open( evalLumDir, 'r')
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
                lumFid.write( '        L_m of lane ' + str( lane ) + ':            ' + str( L_m_lane ) + '\n')
                print '        L_min of lane ' + str( lane ) + ':        ' + str( L_min__[lane] )
                lumFid.write( '        L_min of lane ' + str( lane ) + ':        ' + str( L_min__[lane] ) + '\n')
                print '        L_max of lane ' + str( lane ) + ':        ' + str( L_max_lane )
                lumFid.write( '        L_max of lane ' + str( lane ) + ':        ' + str( L_max_lane ) + '\n')
                print '        U_0 of lane ' + str( lane ) + ':            ' + str( U_0__)
                lumFid.write( '        U_0 of lane ' + str( lane ) + ':            ' + str( U_0__) + '\n')
                
                L_l_m_.append( L_l_m_lane / L_l_values )
                L_l_m_lane = L_l_m_lane / L_l_values
                L_l_min_lane = min( L_l )
                L_l_min_.append( L_l_min_lane )
                U_l_.append( L_l_min_lane / L_l_m_lane )
                
                print '        L_m lengthwise of lane ' + str( lane ) + ':    ' + str( L_l_m_lane )
                lumFid.write('        L_m lengthwise of lane ' + str( lane ) + ':    ' + str( L_l_m_lane ) + '\n')
                print '        L_min lengthwise of lane ' + str( lane ) + ':    ' + str( L_l_min_[lane] )
                lumFid.write('        L_min lengthwise of lane ' + str( lane ) + ':    ' + str( L_l_min_[lane] ) + '\n')
                print '        L_max lengthwise of lane ' + str( lane ) + ':    ' + str( max( L_l ) )
                lumFid.write('        L_max lengthwise of lane ' + str( lane ) + ':    ' + str( max( L_l ) ) + '\n')
                print '        U_l of lane ' + str( lane ) + ':            ' + str( U_l_[lane] )
                lumFid.write('        U_l of lane ' + str( lane ) + ':            ' + str( U_l_[lane] ) + '\n')
                
                lumFile.close( )
            
            L_m = L_m / self.roadScene.scene.road.numLanes
            L_m_.append( L_m )
            L_min_ = min( L_min__ )
            U_0_.append( L_min_ / L_m )
            U_l = min( U_l_ )
            
            print('    Values of all Lanes:')
            lumFid.write('    Values of all Lanes:'+ '\n')
            print '    L_m = ' + str( L_m )
            lumFid.write('    L_m = ' + str( L_m ) + '\n')
            print '    L_min = ' + str( L_min_ )
            lumFid.write('    L_min = ' + str( L_min_ ) + '\n')
            print '    L_max = ' + str( max( L ) )
            lumFid.write('    L_max = ' + str( max( L ) ) + '\n')
            print '    U_0 = ' + str( L_min_ / L_m )
            lumFid.write('    U_0 = ' + str( L_min_ / L_m ) + '\n')
            print '    U_l = ' + str( U_l )
            lumFid.write('    U_l = ' + str( U_l ) + '\n')
        
        Evaluator.meanLuminance = min( L_m_ )
        Evaluator.uniformityOfLuminance = min( U_0_)
        Evaluator.lengthwiseUniformityOfLuminance = min( U_l_ )
        
        print('Min of all Lanes & Viewers:')
        lumFid.write('Min of all Lanes:'+ '\n')
        print 'L_m = ' + str( Evaluator.meanLuminance )
        lumFid.write('L_m = ' + str( Evaluator.meanLuminance ) + '\n')
        print 'L_min = ' + str( min( L_min__ ) )
        lumFid.write('L_min = ' + str( min( L_min__ ) ) + '\n')
        print 'L_max = ' + str( max( L ) )
        lumFid.write('L_max = ' + str( max( L ) ) + '\n')
        print 'U_0 = ' + str( min( U_0_) )
        lumFid.write('U_0 = ' + str( min( U_0_) ) + '\n')
        print 'U_l = ' + str( min( U_l_ ) )
        lumFid.write('U_l = ' + str( min( U_l_ ) ) + '\n')
        
        print "Done."            
        
    def evalIlluminance( self ):
        print 'Evaluate illuminances...'      
        
        if( not os.path.isdir( self.xmlConfigPath + Evaluator.evalDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Evaluator.evalDirSuffix )
        
        illumFid = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/Evaluation_Illuminance', 'w+' )
        
        E_min_ = []
        E_m_ = 0
        g_1_ = []
                
        for lane in range( self.roadScene.scene.road.numLanes ):
            print '    lane: ' + str( lane )
            illumFid.write('    lane: ' + str( lane ) + '\n')
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
            illumFid.write('        E_m of lane ' + str( lane ) + ':            ' + str( E_m_lane ) + '\n')
            print '        E_min of lane ' + str( lane ) + ':        ' + str( E_min_[lane] )
            illumFid.write('        E_min of lane ' + str( lane ) + ':        ' + str( E_min_[lane] ) + '\n')
            print '        E_max of lane ' + str( lane ) + ':        ' + str( max( E ) )
            illumFid.write('        E_max of lane ' + str( lane ) + ':        ' + str( max( E ) ) + '\n')
            print '        g_1 of lane ' + str( lane ) + ':            ' + str( g_1_[lane] )
            illumFid.write('        g_1 of lane ' + str( lane ) + ':            ' + str( g_1_[lane] ) + '\n')
            
            lumFile.close( )
                
        E_m = E_m_ / self.roadScene.scene.road.numLanes
        E_min = min( E_min_ )
        g_1 = E_min / E_m
        
        print '    E_m = ' + str( E_m )
        illumFid.write('    E_m = ' + str( E_m ) + '\n')
        print '    E_min = ' + str( E_min)
        illumFid.write('    E_min = ' + str( E_min) + '\n')
        print '    E_max = ' + str( max( E ) )
        illumFid.write('    E_max = ' + str( max( E ) ) + '\n')
        print '    g_1 = ' + str( g_1 )
        illumFid.write('    g_1 = ' + str( g_1 ) + '\n')
        
        Evaluator.meanIlluminance = E_m
        Evaluator.minIlluminance = E_min        
        Evaluator.uniformityOfIlluminance = g_1
        
        print '    done ...'
        print ''    
        
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
        
        print '    done ...'
        print ''   
    
    def evalVeilingLuminance( self, mode, type ):
        # type = fixed, withTarget or off
        # function calculate veiling luminance
        # function calls addLvToLMKSetMat()
        print 'Generate veiling luminance' 
        
        streetLightArray = []
        headlightFixedArray = []
        headlightVarArray = []
        
        existingVarHeadlight = False
        existingFixedHeadlight = False
        
        for measPointCounter in range( self.TI.numberOfMeasurementPoints ):
            
            streetLightArrayHelp = []
            headlightFixedArrayHelp = []
            headlightVarArrayHelp = []

            for lightsCounter in range( self.TI.tiArray[ measPointCounter ].__len__() ):
                # filter array: only streetlights
                if( self.TI.tiArray[ measPointCounter ][ lightsCounter ].type == "light" ):
                    streetLightArrayHelp.append( self.TI.tiArray[ measPointCounter ][ lightsCounter ] )
                else:
                    # filter array: only with fixed headlights
                    if( self.TI.tiArray[ measPointCounter ][ lightsCounter ].headlightType == "fixed" ):
                        headlightFixedArrayHelp.append( self.TI.tiArray[ measPointCounter ][ lightsCounter ] )
                        existingFixedHeadlight = True
                    # filter array: only with var headlights
                    else:
                        headlightVarArrayHelp.append( self.TI.tiArray[ measPointCounter ][ lightsCounter ] )
                        existingVarHeadlight = True
            
            streetLightArray.append( streetLightArrayHelp )
            headlightFixedArray.append( headlightFixedArrayHelp )
            headlightVarArray.append( headlightVarArrayHelp )
        
        veilingLumSLArray = self.getVeilingLumArray( streetLightArray )
        L_v_SL_Array = [ x * self.TI.ageFactor for x in veilingLumSLArray ]

        if( existingFixedHeadlight ):
            veilingLumFixedArray = self.getVeilingLumArray( headlightFixedArray )
            #combineArrays = [ veilingLumSLArray[ x ] + veilingLumFixedArray[ x ] for x in range( 0, len( veilingLumSLArray ) ) ]
            L_v_fixed_Array = [ x * self.TI.ageFactor for x in veilingLumFixedArray ]
        
        if( existingVarHeadlight ):
            veilingLumVarArray = []
            for measPointCounter in range( self.TI.numberOfMeasurementPoints ):
                veilingLumHelpArray = []
                for lightsCounter in range( 0, headlightVarArray[ measPointCounter ].__len__(), 2 ):
                    # one Lv value for each pair of headlight left and right
                    L_v_1 = headlightVarArray[ measPointCounter ][ lightsCounter ].veilingLum
                    L_v_2 = headlightVarArray[ measPointCounter ][ lightsCounter + 1 ].veilingLum
                    L_v_perMeaspoint = ( L_v_1 + L_v_2 ) * self.TI.ageFactor
                    veilingLumHelpArray.append( L_v_perMeaspoint )
                veilingLumVarArray.append( veilingLumHelpArray )
        
        if not( existingFixedHeadlight and existingVarHeadlight ):
            print '    no headlights detected '
        
        print ''
        print 'Calculate veiling luminance'
        
        ## calculate veiling luminance
        L_v_measAll_SL = 0.0
        L_v_measAll_fixed = 0.0
        L_v_measAll_var = 0.0
        
        if( self.TI.numberOfMeasurementPoints == L_v_SL_Array.__len__() ): 
            for measPoint in range( self.TI.numberOfMeasurementPoints ):
                L_v_measAll_SL += L_v_SL_Array[ measPoint ]
                if( existingFixedHeadlight ):
                    L_v_measAll_fixed += L_v_fixed_Array[ measPoint ]
                if( existingVarHeadlight ):
                    valuePerMeas = 0.0
                    for drivingCar in range( veilingLumVarArray[ measPoint ].__len__() ):
                        valuePerMeas += veilingLumVarArray[ measPoint ][ drivingCar ]
                    meanValuePerMeas = valuePerMeas / veilingLumVarArray[ measPoint ].__len__()
                    L_v_measAll_var += meanValuePerMeas
                    
            Evaluator.L_v_SL = L_v_measAll_SL / self.TI.numberOfMeasurementPoints
            Evaluator.L_v_fixed = L_v_measAll_fixed / self.TI.numberOfMeasurementPoints
            Evaluator.L_v_var = L_v_measAll_var / self.TI.numberOfMeasurementPoints
            
            print '    L_v_SL_' + str( mode )+ ': ' + str( Evaluator.L_v_SL )
            print '    L_v_fixed_' + str( mode )+ ': ' + str( Evaluator.L_v_fixed )
            print '    L_v_var_' + str( mode )+ ': ' + str( Evaluator.L_v_var )
            
        else:
            print '! an ERROR occured array length not same length of measurement points'
        
        # call function addLvToLMKSetMat and add specific data 
        print '    call function addLvToLMKSetMat with type: ' + str( type )
        print ''
        
        if( ( type == "fixed") and existingFixedHeadlight ):
            self.addLvToLMKSetMat( L_v_SL_Array, L_v_fixed_Array, headlightFixedArray, False, False, mode, type )
        elif( ( type == "withTarget") and existingVarHeadlight ):
            if( existingFixedHeadlight ):
                self.addLvToLMKSetMat( L_v_SL_Array, L_v_fixed_Array, headlightFixedArray, veilingLumVarArray, headlightVarArray , mode, type )
            else:
                self.addLvToLMKSetMat( L_v_SL_Array, False, False, veilingLumVarArray, headlightVarArray , mode, type )
        else:
            self.addLvToLMKSetMat( L_v_SL_Array, False, False, False, False, mode, type )
        
    def getVeilingLumArray( self, filteredArray ):
        
        veilingLumArray = []
        
        for measPointCounter in range( self.TI.numberOfMeasurementPoints ):
            L_v_perMeaspoint = 0.0
            for lightsCounter in range( filteredArray[ measPointCounter ].__len__() ):
                L_v_perMeaspoint += filteredArray[ measPointCounter ][ lightsCounter ].veilingLum
            veilingLumArray.append( L_v_perMeaspoint )
        
        return veilingLumArray
    
    def veilingLuminanceForMode( self, mode ):
        # calculate all single veiling luminance values in self.TI.tiArray
        print 'Calculate veiling luminance values for mode: ' + str( mode )
        
        for measPointCounter in range( self.TI.numberOfMeasurementPoints ): 
            for lightsCounter in range( self.TI.tiArray[ measPointCounter ].__len__() ):
                # calculate exponent n of theta as defined in RP800
                if( self.TI.tiArray[ measPointCounter ][ lightsCounter ].theta < 2 ):
                    n = 2.3 - 0.7 * math.log10( self.TI.tiArray[ measPointCounter ][ lightsCounter ].theta )
                else:
                    n = 2
                
                if( mode == "RP800"):
                    self.TI.tiArray[ measPointCounter ][ lightsCounter ].veilingLum = self.TI.tiArray[ measPointCounter ][ lightsCounter ].illuminance / self.TI.tiArray[ measPointCounter ][ lightsCounter ].theta**n
                else:
                    self.TI.tiArray[ measPointCounter ][ lightsCounter ].veilingLum = self.TI.tiArray[ measPointCounter ][ lightsCounter ].illuminance / self.TI.tiArray[ measPointCounter ][ lightsCounter ].theta**2

        print 'Done.'
        print ''
                    
    def evalThresholdIncrement( self, mode ):
        print 'Evaluate Threshold Increment'
        print '    mean Luminance: ' + str( Evaluator.meanLuminance )
        print '    AgeFactor: ' + str( self.TI.ageFactor ) 
        
        Evaluator.tiSL = 65 * Evaluator.L_v_SL / Evaluator.meanLuminance**0.8
        Evaluator.tiFixed = 65 * Evaluator.L_v_fixed / Evaluator.meanLuminance**0.8
        Evaluator.tiVar = 65 * Evaluator.L_v_var / Evaluator.meanLuminance**0.8
        print '    Threshold Increment SL ' + str( mode ) + ': ' + "%.2f" % Evaluator.tiSL + ' %'
        print '    Threshold Increment fixed ' + str( mode ) + ': ' + "%.2f" % Evaluator.tiFixed + ' %'
        print '    Threshold Increment var ' + str( mode ) + ': ' + "%.2f" % Evaluator.tiVar + ' %'
        
        print '    done ...'
        print ''  
    
    def addLvToLMKSetMat( self, L_v_SL_Array, L_v_fixed_Array, headlightFixedArray, veilingLumVarArray, headlightVarArray , mode, type ):
        # problem numberOfSubimages(14) /= numberOfMeasurementPoints(10)
        # 2 pics before measfield and 2 after, how to add to LMKSetMat
        # DEBUG check if numberOfSubimages and numberOfMeasurementPoints make sense and fit function!
        
        print 'Add Veiling Lum to LMKSetMat'
        print '    mode: ' + str( mode ) + ' and type: ' + str( type ) 
        LMKSetMat = '/' + os.path.basename( self.xmlConfigPath ) # '/LMKSetMat'
        print '    LMKSetMat path: ' + self.xmlConfigPath + LMKSetMat
        
        input = open( self.xmlConfigPath + LMKSetMat + '/LMKSetMat.xml', "r" )
        output = open( self.xmlConfigPath + LMKSetMat + '/LMKSetMat2.xml', "w" )
        
        print '    Number of Veiling Luminance Values: ' + str( len( L_v_SL_Array ) )
        print '    Number of SubImages: ' + str( self.roadScene.numberOfSubimages )
        print '    Number of Measurement Points: ' + str( self.TI.numberOfMeasurementPoints )
        
        # DEBUG gibt es Werte die nicht gültig sind???
        counterMin = self.roadScene.numberOfSubimages - self.TI.numberOfMeasurementPoints
        counterMax = self.roadScene.numberOfSubimages - counterMin + 1
        counter = 0
        for line in input:
            output.write( line )
            if( line.lstrip().startswith( '</RectObject>' )):
                counter += 1
                if( ( counter > counterMin ) and ( counter < counterMax ) ):
                    output.write( '<veilingLuminances> \n' )
                    output.write( '<veilingLuminance Lv="' + str( L_v_SL_Array[ counter - ( counterMin + 1 ) ] ) + '" type="streetlight"/> \n' )
                    if( type == "fixed" ):
                        output.write( '<veilingLuminance Lv="' + str( L_v_fixed_Array[ counter - ( counterMin + 1 ) ] ) + '" type="fixedHeadlight "/> \n' )
                    elif( type == "withTarget" ):
                        if( L_v_fixed_Array == False ):
                            for valuesPerMeas in range( veilingLumVarArray[ counter - ( counterMin + 1 ) ].__len__() ):
                                output.write( '<veilingLuminance Lv="' + str( veilingLumVarArray[ counter - ( counterMin + 1 ) ][ valuesPerMeas ] ) + '" type="variableHeadlight" position="' + str( headlightVarArray[ counter - ( counterMin + 1 ) ][ valuesPerMeas * 2 ].positionY ) + '"/> \n' )
                        else:
                            output.write( '<veilingLuminance Lv="' + str( L_v_fixed_Array[ counter - ( counterMin + 1 ) ] ) + '" type="fixedHeadlight "/> \n' )
                            for valuesPerMeas in range( veilingLumVarArray[ counter - ( counterMin + 1 ) ].__len__() ):
                                output.write( '<veilingLuminance Lv="' + str( veilingLumVarArray[ counter - ( counterMin + 1 ) ][ valuesPerMeas ] ) + '" type="variableHeadlight" position="' + str( headlightVarArray[ counter - ( counterMin + 1 ) ][ valuesPerMeas * 2 ].positionY ) + '"/> \n' )
                        
                    output.write( '</veilingLuminances> \n' )
                else:
                    output.write( '<veilingLuminances> \n' )
                    output.write( '<veilingLuminance Lv="0"/> \n' )
                    output.write( '</veilingLuminances> \n' )
                    
        input.close()
        output.close()
        
        print '    done ...'
        print '' 
            
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
        
        ti_element = doc.createElement( "ThresholdIncremnt" )
        doc.documentElement.appendChild( ti_element )
        
        tiValue_element = doc.createElement( "tiValues" )
        tiValue_element.setAttribute( 'TI_streetlight_' + str( self.roadScene.scene.calculation.veilingLuminanceMethod ) , str( Evaluator.tiSL ) )
        tiValue_element.setAttribute( 'TI_fixedHeadlight_' + str( self.roadScene.scene.calculation.veilingLuminanceMethod ) , str( Evaluator.tiFixed ) )
        tiValue_element.setAttribute( 'TI_variableHeadlight_' + str( self.roadScene.scene.calculation.veilingLuminanceMethod ) , str( Evaluator.tiVar ) )
        ti_element.appendChild( tiValue_element )
        
        veilingLum_element = doc.createElement( "veilingLuminances" )
        veilingLum_element.setAttribute( 'L_v_streetlight_' + str( self.roadScene.scene.calculation.veilingLuminanceMethod ), str( Evaluator.L_v_SL ) )
        veilingLum_element.setAttribute( 'L_v_fixedHeadlight_' + str( self.roadScene.scene.calculation.veilingLuminanceMethod ), str( Evaluator.L_v_fixed ) )
        veilingLum_element.setAttribute( 'L_v_variableHeadlight_' + str( self.roadScene.scene.calculation.veilingLuminanceMethod ), str( Evaluator.L_v_var ) )

        ti_element.appendChild( veilingLum_element )
        
        f = open( self.xmlConfigPath + Evaluator.evalDirSuffix + '/Evaluation.xml', "w" )
        doc.writexml( f, "", "    ")
        f.close( )           
        
        print '    done ...'
        print ''
            
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
        
        print '    done ...'
        print ''