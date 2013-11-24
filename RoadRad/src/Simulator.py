# This Python file uses the following encoding: utf-8

import os
import datetime
import Image
import ImageDraw
import math
import csv
import struct
import shutil
import sys
from select import select
import Classes.RoadScene as modulRoadscene
#user input ambient calculation timer
import thread
import threading
#import pymorph


#write a few documentation
class Simulator:

    # output image resolution
    horizontalRes = 1380
    verticalRes = 1030
    # true or false for falsecolor picture
    makeFalsecolor = False
    # folder suffixes
    octDirSuffix = '/Octs'
    refOctDirSuffix = '/RefOcts'
    radDirSuffix = '/Rads'
    refPicDirSuffix = '/RefPics'
    picDirSuffix = '/Pics'
    lidcSuffix = '/LIDCs'
    picSubDirSuffix = '/pics'
    falsecolorSubDirSuffix = '/falsecolor'
    pfSubDirSuffix = '/pfs'
    lumSubDirSuffix = '/lums'
    
    LMKSetMatFilename = '/LMKSetMat.xml'
    
    def __init__( self, path, RefPic ):
        
        self.willSkipRefPic = RefPic
        self.xmlConfigPath = path
        self.xmlConfigName = "SceneDescription.xml"
        
        # initialize the roadScene object
        self.roadScene = modulRoadscene.RoadScene( self.xmlConfigPath, self.xmlConfigName )
        
        self.LMKSetMat = '/' + os.path.basename( self.xmlConfigPath ) # '/LMKSetMat'
        print '---- DIR of LMKSetMat: ' + str( self.LMKSetMat )
        
        if( not os.path.isdir( self.xmlConfigPath + self.LMKSetMat ) ):
            os.mkdir( self.xmlConfigPath + self.LMKSetMat )
            
        shutil.copy( self.xmlConfigPath + "/SceneDescription.xml", self.xmlConfigPath + self.LMKSetMat )
        shutil.copy( os.getcwd( ) + "/LMKSetMat.dtd", self.xmlConfigPath + self.LMKSetMat ) # copy DTD for LMKSetMat XML
        
        self.checkTargetAndConfig( ) 
        self.makeOct( )
        self.makePic( )
        self.makeFalsecolorPic( )
        if( not self.willSkipRefPic ):
            self.makeRefPic( )
            self.processRefPics( )
        self.postRenderProcessing( )
        self.deleteUnnecessaryFiles( )
        
    def checkTargetAndConfig( self ):
        path = self.xmlConfigPath + Simulator.radDirSuffix
        dirList = os.listdir( path )
        targetCount = 0
        for file in dirList:
            if( file.startswith( "target_" ) ):
                targetCount = targetCount + 1

        if self.roadScene.numberOfSubimages == targetCount:
            print 'found ' + str( targetCount ) + ' target files with subimages.'
        else:
            print 'found ' + str( targetCount ) + ' targets but ' + str( self.roadScene.numberOfSubimages ) + ' subimages!'
            sys.exit( 0 )
    
    # system call to radiance framework to generate oct files out of the various rads
    # both for the actual simulated image and the refernce pictures to determine the 
    # pixel position of the target objects
    def makeOct( self ):
        if( not os.path.isdir( self.xmlConfigPath + Simulator.octDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Simulator.octDirSuffix )

        if ( self.roadScene.headlights.headlights.__len__() > 0 ):
            fixedHeadlight = False
            varHeadlight = False
            for index, headlightArray in enumerate( self.roadScene.headlights.headlights ):
                if( headlightArray.headlightDistanceMode == 'fixedHeadlightPosition' ):
                    fixedHeadlight = True
                else:
                    varHeadlight = True
            print '----status of fixedHeadlight: ' + str( fixedHeadlight )
            print '----status of varHeadlight: ' + str( varHeadlight )
            
            if ( fixedHeadlight and varHeadlight ):
                for i in range( self.roadScene.numberOfSubimages ):
                    cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/headlight.rad {0}/headlight{1}.rad {0}/target_{1}.rad {0}/night_sky.rad > {2}/scene{1}.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, i, self.xmlConfigPath + Simulator.octDirSuffix )
                    os.system( cmd )
                    print 'generated oct# ' + str( i )
                # without targets in scene.oct
                cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/headlight.rad {0}/headlight0.rad {0}/night_sky.rad > {1}/scene.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, self.xmlConfigPath + Simulator.octDirSuffix )
                os.system( cmd )
                
            elif ( fixedHeadlight and not varHeadlight ):
                for i in range( self.roadScene.numberOfSubimages ):
                    cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/headlight.rad {0}/target_{1}.rad {0}/night_sky.rad > {2}/scene{1}.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, i, self.xmlConfigPath + Simulator.octDirSuffix )
                    os.system( cmd )
                    print 'generated oct# ' + str( i )
                # without targets in scene.oct
                cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/headlight.rad {0}/night_sky.rad > {1}/scene.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, self.xmlConfigPath + Simulator.octDirSuffix )
                os.system( cmd )
                
            elif ( not fixedHeadlight and varHeadlight ):
                for i in range( self.roadScene.numberOfSubimages ):
                    cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/headlight{1}.rad {0}/target_{1}.rad {0}/night_sky.rad > {2}/scene{1}.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, i, self.xmlConfigPath + Simulator.octDirSuffix )
                    os.system( cmd )
                    print 'generated oct# ' + str( i )
                # without targets in scene.oct
                cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/headlight0.rad {0}/night_sky.rad > {1}/scene.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, self.xmlConfigPath + Simulator.octDirSuffix )
                os.system( cmd )
                
            else:
                print 'An error occured at generating oct: invalid headlights data'
                
        else:
            for i in range( self.roadScene.numberOfSubimages ):
                cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/target_{1}.rad {0}/night_sky.rad > {2}/scene{1}.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, i, self.xmlConfigPath + Simulator.octDirSuffix )
                os.system(cmd)
                print 'generated oct# ' + str( i )
            # without targets in scene.oct
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/night_sky.rad > {1}/scene.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, self.xmlConfigPath + Simulator.octDirSuffix )
            os.system(cmd)
        
        # generate octs for reference pics
        if( not self.willSkipRefPic ):
            if( not os.path.isdir( self.xmlConfigPath + Simulator.refOctDirSuffix ) ):
                os.mkdir( self.xmlConfigPath + Simulator.refOctDirSuffix )
            
            for i in range( self.roadScene.numberOfSubimages ):
                cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/self_target_{1}.rad {0}/night_sky.rad > {2}/scene{1}.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, i, self.xmlConfigPath + Simulator.refOctDirSuffix )
                os.system(cmd)
                print 'generated reference oct# ' + str( i )
            # without targets in scene.oct
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/night_sky.rad > {1}/scene.oct'.format( self.xmlConfigPath + Simulator.radDirSuffix, self.xmlConfigPath + Simulator.refOctDirSuffix )
            os.system(cmd)

    # System call to radiance framework for the actual rendering of the images
    def makePic(self):
        if( not os.path.isdir( self.xmlConfigPath + Simulator.picDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Simulator.picDirSuffix )
        if( not os.path.isdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix )
        if( not os.path.isdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix ) ):
            os.mkdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix )
            
        # choosing between high accurate ambient and normal simulation
        print 'Please enter y(yes) or n(no) for ambient calculation: '
        timeout = 10
        print 'You choose:',
        rlist, _, _ = select([sys.stdin], [], [], timeout)
        if rlist:
            ambCalc = sys.stdin.readline()
            print ambCalc
        else:
            print 'No input. None ambient calculation...'
            ambCalc = 'n'                
        
        for i in range( self.roadScene.numberOfSubimages ):
            print 'generating pic# ' + str( i )
            starttime = datetime.datetime.now()
            cmd0 = ''
            
            if ambCalc == 'y' or ambCalc == 'ye' or ambCalc == 'yes':
                if self.roadScene.targetParameters.viewPoint.targetDistanceMode == 'fixedViewPoint':
                    cmd0 = 'rpict -vtv -vf {3}/eye.vp -x {4} -y {5} -ps 1 -pt 0 -pj 1 -dj 1 -dp 0 -ds .01 -dt 0 -dc 1 -dr 6 -sj 1 -st 0 -ab 5 -aa 0 -ad 4096 -as 1024 -ar 0 -lr 16 -lw 0 {0}/scene{1}.oct > {2}/out{1}.hdr '.format( self.xmlConfigPath + Simulator.octDirSuffix , i, self.xmlConfigPath + Simulator.picDirSuffix +Simulator.picSubDirSuffix, self.xmlConfigPath + Simulator.radDirSuffix, Simulator.horizontalRes, Simulator.verticalRes )                    
                else:
                    cmd0 = 'rpict -vtv -vf {3}/eye{1}.vp -x {4} -y {5} -ps 1 -pt 0 -pj 1 -dj 1 -dp 0 -ds .01 -dt 0 -dc 1 -dr 6 -sj 1 -st 0 -ab 5 -aa 0 -ad 4096 -as 1024 -ar 0 -lr 16 -lw 0 {0}/scene{1}.oct > {2}/out{1}.hdr '.format( self.xmlConfigPath + Simulator.octDirSuffix , i, self.xmlConfigPath + Simulator.picDirSuffix +Simulator.picSubDirSuffix, self.xmlConfigPath + Simulator.radDirSuffix, Simulator.horizontalRes, Simulator.verticalRes )                                         
            else:    
                if self.roadScene.targetParameters.viewPoint.targetDistanceMode == 'fixedViewPoint':
                    cmd0 = 'rpict -vtv -vf {3}/eye.vp -x {4} -y {5} {0}/scene{1}.oct > {2}/out{1}.hdr '.format( self.xmlConfigPath + Simulator.octDirSuffix , i, self.xmlConfigPath + Simulator.picDirSuffix +Simulator.picSubDirSuffix, self.xmlConfigPath + Simulator.radDirSuffix, Simulator.horizontalRes, Simulator.verticalRes )
                else:
                    cmd0 = 'rpict -vtv -vf {3}/eye{1}.vp -x {4} -y {5} {0}/scene{1}.oct > {2}/out{1}.hdr '.format( self.xmlConfigPath + Simulator.octDirSuffix , i, self.xmlConfigPath + Simulator.picDirSuffix +Simulator.picSubDirSuffix, self.xmlConfigPath + Simulator.radDirSuffix, Simulator.horizontalRes, Simulator.verticalRes )
                
            os.system( cmd0 )
            print 'done.'
            print datetime.datetime.now() - starttime

            #include veiling luminance if whished
            if ( self.roadScene.scene.calculation.veilingLuminance == 'on' ):
                print 'generating veiling luminance'
                starttime = datetime.datetime.now()
                glareCmd = 'findglare -c -r 4000 -p {1}/out{0}.hdr > {1}/out{0}_glares.glr'.format( i, self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix ) 
                os.system( glareCmd )
                glareFile = open( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '_glares.glr', 'r' )
                glaresources = open( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '_glaretable.glr', 'a' )
                isGlaresource = 0
                for line in glareFile:
                    begin = 'BEGIN glare source'
                    if begin in line:
                        isGlaresource = 1
                        continue
                    end = 'END glare source'
                    if end in line:
                        isGlaresource = 0
                        break
                    if isGlaresource == 1:
                        glaresources.write( line )
                glareFile.close( )
                glaresources.close( )
                
                xdirection = []
                ydirection = []
                zdirection = []
                illuminance = []
                
                glaretable = open( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '_glaretable.glr', 'r')
                tablereader = csv.reader( glaretable, delimiter = '    ' )
                for row in tablereader:
                    direction = row[1].split( ' ' )
                    xdirection.append( direction[0] )
                    ydirection.append( direction[1]  )
                    zdirection.append( direction[2]  )
                    illuminance.append( float( row[2] ) * float( row[3] ) )
                glaretable.close( )
                
                glares = open( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '_glares.cal', 'a' )
                glares.write( 'SDx(i): select(i, ' + ', '.join( xdirection ) + ' );\n' )
                glares.write( 'SDy(i): select(i, ' + ', '.join( ydirection ) + ' );\n' )
                glares.write( 'SDz(i): select(i, ' + ', '.join( zdirection ) + ' );\n' )
                glares.write( 'I(i): select(i, ' + ', '.join( map( str, illuminance ) ) + ' );\n' )
                glares.write( 'N : I(0);' )
                glares.close( )
                
                veilCmd = 'pcomb -f {1}/out{0}_glares.cal -f {2}/veil.cal {1}/out{0}.hdr > {1}/out{0}_veil.hdr'.format( i, self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix, self.xmlConfigPath + self.radDirSuffix )
                os.system( veilCmd )                    
                
                os.remove( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '_glares.glr' )
                os.remove( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '_glaretable.glr' )
                os.remove( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '_glares.cal' )
                #os.remove( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + '/out' + str( i ) + '.hdr' )
                
                print 'done.'
                print datetime.datetime.now() - starttime
        
        # make pic for view up and down the road
        print 'generating pics for view up and down'
        starttime = datetime.datetime.now()
        cmdUp = 'rpict -x 500 -y 500 -vf {2}/eye_up.vp {0}/scene.oct > {1}/out_up.hdr '.format( self.xmlConfigPath + self.octDirSuffix, self.xmlConfigPath + self.picDirSuffix + Simulator.picSubDirSuffix, self.xmlConfigPath + self.radDirSuffix )
        os.system( cmdUp )
        cmdUpTiff = 'ra_tiff -e +8 {0}/out_up.hdr {0}/out_up.tiff'.format( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix )
        os.system( cmdUpTiff)
        cmdDown = 'rpict -x 2000 -y 2000 -vf {2}/eye_down.vp {0}/scene.oct > {1}/out_down.hdr '.format( self.xmlConfigPath + self.octDirSuffix, self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix, self.xmlConfigPath + self.radDirSuffix )
        os.system( cmdDown )
        cmdDownTiff = 'ra_tiff -e +8 {0}/out_down.hdr {0}/out_down.tiff'.format( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix )
        os.system( cmdDownTiff)
        #os.remove( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + "/out_up.hdr" )
        #os.remove( self.xmlConfigPath + self.picDirSuffix + self.picSubDirSuffix + "/out_down.hdr" )
        print 'done.'
        print datetime.datetime.now() - starttime
             
    # System call to radiance framework for creating a falsecolor image
    def makeFalsecolorPic(self):  
        if self.makeFalsecolor == True:
            for i in range( self.roadScene.numberOfSubimages ):
                print 'generating falsecolor pic# ' + str( i )
                starttime = datetime.datetime.now()
                cmd0 = 'falsecolor -i {1}/out{0}.hdr -log 5 -l cd/m^2 > {2}/false_out{0}.hdr'.format( i, self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix, self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix )
                #cmd1 = 'falsecolor -i {1}/out{0}.hdr -cl -log 5 > {2}/falseContour_out{0}.hdr'.format( i, self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix, self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix )
                os.system( cmd0 )
                #os.system( cmd1 )
                cmd2 = 'ra_tiff {1}/false_out{0}.hdr {2}/false_out{0}.tiff'.format( i, self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix, self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix )
                os.system( cmd2 )
                
                print 'done.'
                print datetime.datetime.now() - starttime
            
            dirList = os.listdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix )
            for file in dirList:
                if( file.endswith( ".hdr" ) ):
                    os.remove( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.falsecolorSubDirSuffix + "/" + file )
    
    # system call to render the refernce images
    def makeRefPic(self):
        if( not os.path.isdir( self.xmlConfigPath + Simulator.refPicDirSuffix ) ):
                os.mkdir( self.xmlConfigPath + Simulator.refPicDirSuffix )
        
        for i in range( self.roadScene.numberOfSubimages ):
                print 'generating Reference pic# ' + str( i )
                starttime = datetime.datetime.now()
                
                cmd0 = ''
                if ( self.roadScene.targetParameters.viewPoint.targetDistanceMode == 'fixedViewPoint' ):
                    cmd0 = 'rpict -vtv -vf {3}/eye.vp -x {4} -y {5} {0}/scene{1}.oct > {2}/out{1}.hdr '.format( self.xmlConfigPath + Simulator.refOctDirSuffix , i, self.xmlConfigPath + Simulator.refPicDirSuffix, self.xmlConfigPath + Simulator.radDirSuffix, Simulator.horizontalRes, Simulator.verticalRes )
                else:
                    cmd0 = 'rpict -vtv -vf {3}/eye{1}.vp -x {4} -y {5} {0}/scene{1}.oct > {2}/out{1}.hdr '.format( self.xmlConfigPath + Simulator.refOctDirSuffix , i, self.xmlConfigPath + Simulator.refPicDirSuffix, self.xmlConfigPath + Simulator.radDirSuffix, Simulator.horizontalRes, Simulator.verticalRes )
                    
                cmd1 = 'ra_tiff {0}/out{1}.hdr {0}/out{1}.tiff'.format( self.xmlConfigPath + Simulator.refPicDirSuffix, i )
                os.system( cmd0 )
                os.system( cmd1 )
                print 'done.'
                print datetime.datetime.now() - starttime
            
                #cmd1 = 'rpict -vtv -vp 18 -273 4.75 -vd 0 0.999856 -0.0169975 -vu 0 0 1 -vh 6 -vv 3 -vs 0 -vl 0 -x 3000 -y 1500 {0}/scene.oct | pfilt -r .6 -x 800 -y 400 -1 -e 5 > {0}/scene1.pic'.format( entry )
                #os.system( cmd1 )
            
                #cmd2 = 'rpict -x 500 -y 2000 -vtl -vp 18 -150 4 -vd 0 0 -1 -vu 0 1 0 -vh 100 -vv 400 -vs 0 -vl 0 {0}/scene.oct | pfilt -x 200 -y 800 -r .6 -1 -e 200 > {0}/scene2.pic'.format( entry )
                #print cmd
                #os.system( cmd2 )
    
    # Here the reference pictures are parsed pixel wise using the python image library.
    # The self glowing target object is isolated and outputted in the defined xml format.
    def processRefPics( self ):
        print "Processing reference pics."
        
        targetDistance = []
        
        targetFile = open( self.xmlConfigPath + Simulator.radDirSuffix + '/targetdistances.txt' )
        for line in targetFile.readlines( ):
            targetDistance.append( float( line.strip( '\n' ) ) )
        targetFile.close( )
        
        if( not os.path.isdir( self.xmlConfigPath + self.LMKSetMat ) ):
            os.mkdir( self.xmlConfigPath + self.LMKSetMat )
        
        xmlOut = open( self.xmlConfigPath + self.LMKSetMat + self.LMKSetMatFilename, 'w' )
        xmlOut.write( "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<!DOCTYPE LMKSetMat SYSTEM \"LMKSetMat.dtd\">\n\n<LMKSetMat>\n" )
        xmlOut.write( "<Description>\n<SceneTitle Title=\"" + str( self.roadScene.scene.description.title ) + "\"/>\n<FocalLength FL=\"" + str( self.roadScene.scene.description.focalLength ) + "\"/>\n<ViewPoint Distance=\"" + str( self.roadScene.targetParameters.viewPoint.distance ) + "\"/>\n<Target Size=\"" + str( self.roadScene.targetParameters.target.size ) + "\"/>\n" )
        for entry in self.roadScene.lidcs.lidcs:
            xmlOut.write( "<LIDC Name=\"" + str( entry.name ) + "\"/>\n<ScotopicToPhotopicRatio SPRatio=\"" + str( entry.spRatio ) + "\"/>\n" )
        xmlOut.write( "<Pole NumPoleFields=\"" + str( self.roadScene.scene.road.numPoleFields ) + "\"/>\n</Description>\n\n" )
                
        for i in range( self.roadScene.numberOfSubimages ):
            im = Image.open( self.xmlConfigPath + Simulator.refPicDirSuffix + '/out' + str( i ) + '.tiff' )
            pix = im.load( )
            
            width, height = im.size
            
            xmin = 0
            xmax = 0
            ymin = 0
            ymax = 0
            THRESH = 100
            
            #this is the ragged approach of detecting the rectangle of the target
            #does not work very well yet...
            
            #TODO: better mark all connected components and extract the coordinates of the biggest rect
            
            #f=binary(to_uint8([
            #[1, 1, 0, 0, 0, 0, 1],
            #[1, 0, 1, 1, 1, 0, 1],
            #[0, 0, 0, 0, 1, 0, 0]]))
            #y=areaopen(f,4,secross())
            #print y
            #pymorph.dilate(f, B={3x3 cross})
            
            #make image to grayscale
            #pix = im.convert("L")

            for x in range(width):
                for y in range(height):
                    #this checks if each value in each channels of the current pixel is above the certain threshold
                    if( pix[ x, y ][ 0 ] > THRESH and pix[ x, y ][ 1 ] > THRESH and pix[ x, y ][ 2 ] > THRESH ):
                        if( xmin == 0 ):
                            xmin = x
                        else:
                            if ( x > xmax ):
                                xmax = x
                            
                        if( ymin == 0 ):                            
                            ymin = y
                        else:
                            if ( y > ymax ):
                                ymax = y
                            
                    #if( i == 11 and xmin != 0 ):
                        #print str( xmax )
            
            #debug: save region to image:
            #draw.line(xy, options)
            width = xmax - xmin
            height = ymax - ymin
            im2 = Image.open( self.xmlConfigPath + Simulator.refPicDirSuffix + '/out' + str(i) + '.tiff' )
            im2.convert( 'RGB' )
            draw = ImageDraw.Draw( im2 )
            draw.rectangle( [ ( xmin, ymin ), ( xmax, ymax ) ], fill='red')
            im2.save( self.xmlConfigPath + Simulator.refPicDirSuffix + '/debug_output' + str(i) + '.tif' )
            
            #prepare xml rect positions for use in matlab (offset of 1 pixel)
            xminRect = xmin + 1
            yminRect = ymin + 1
            xmaxRect = xmax + 1
            ymaxRect = ymax + 1
            
            xmlOut.write( "<LMKData>\n<dataSource src=\"out" + str( i ) + ".pf\" type=\"pf_photopic\"/>\n<RectObject>\n<upperLeft x=\"" + str( xminRect ) + "\" y=\"" + str( yminRect ) + "\"/>\n<lowerRight x=\"" + str( xmaxRect ) + "\" y=\"" + str( ymaxRect ) + "\"/>\n<border pixel=\"2\"/>\n<position p=\"" + str( targetDistance[ i ] ) + "\"/>\n</RectObject>\n</LMKData>\n\n" )
        
        xmlOut.write( "</LMKSetMat>" )
        xmlOut.close( )          
        return
    
    #Here the generated hdr images are converted to the pf format.
    #This involves using pvalue(radiance) to determine the luminance values of each pixel (-b option 
    #gives radiance values, rcalc converts them to luminance values.
    #These values are dumped into a text file. the text file is then parsed and
    #are written into the final binary output pf file with the predefined header.
    def postRenderProcessing( self ):
        #create direction for temporarily save luminance txt files
        if( not os.path.isdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix + Simulator.lumSubDirSuffix ) ):
                os.mkdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix + Simulator.lumSubDirSuffix )
        
        #find all .hdr images named "out[i].hdr in pics directory
        processingList = []
        dirList = os.listdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix )
        for entry in dirList:
            if( not os.path.isdir( entry ) ):
                if( "out" and "hdr" in entry ):
                    processingList.append( entry )
        
        #using pvalue (radiance) to determine the luminance values of each pixel (-b option 
        #gives radiance values, rcalc converts them to luminance values) and save them into txt file.
        print "dumping pvalues:"
        for pic in processingList:
            print "File: " + pic
            cmd = "pvalue -h -H -b " + self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix + '/' +pic + " | rcalc -e '$1=179*$3' > " + self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix + Simulator.lumSubDirSuffix + '/' + pic.replace( ".hdr", ".txt" )
            os.system(cmd)
            print "done."
        
        #find all txt files containing luminance values
        processedList = []
        dirList2 = os.listdir( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix + Simulator.lumSubDirSuffix )
        for entry in dirList2:
            if( not os.path.isdir( entry ) ):
                if( "out" in entry ):
                    processedList.append( entry )
                    
        #write all luminance values into binary pf file and add predefined header
        print "converting to .pf format"
        for txtFile in processedList:
            print "File: " + txtFile.replace( ".txt", ".pf" )
            imgData = []
            lumFile = open( self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix + Simulator.lumSubDirSuffix + '/' + txtFile, 'r')
            rgbReader = csv.reader( lumFile, delimiter = ' ' )
            for row in rgbReader:
                pixelData = []
                for item in row:
                    if( len(item ) != 0 ):
                        pixelData.append( float( item ) )
                imgData.append( pixelData )
            lumFile.close()
            
            pfOut = open( str( self.xmlConfigPath + self.LMKSetMat + '/' + txtFile.replace( ".txt", ".pf" ) ), 'wb' )
            cmd = 'Typ=Pic98::TPlane<float>\r\nLines={1}\r\nColumns={0}\r\nFirstLine=1\r\nFirstColumn=1\r\n\0'.format(Simulator.horizontalRes ,Simulator.verticalRes)
            pfOut.write( cmd )
            
            for pixel in imgData: 
                pfOut.write( struct.pack( 'f', pixel[0] ) )
            
            pfOut.close()
            print "done"                
        return
        
                #clean up and delete txt files
    def deleteUnnecessaryFiles( self ):
        rbgPath = self.xmlConfigPath + Simulator.picDirSuffix + Simulator.picSubDirSuffix + Simulator.lumSubDirSuffix
        if( os.path.exists( rbgPath ) ):
            shutil.rmtree( rbgPath )
        
        return
