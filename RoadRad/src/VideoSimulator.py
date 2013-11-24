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


#write a few documentation
class VideoSimulator:

    # output image resolution
    horizontalRes = 1380
    verticalRes = 1030
    # folder suffixes
    octDirSuffix = '/Octs'
    radDirSuffix = '/Rads'
    picDirSuffix = '/Pics'
    picSubDirSuffix = '/pics'
    pfSubDirSuffix = '/pfs'
    lumSubDirSuffix = '/lums'

    def __init__( self, path, speedAndFPS ):

        self.workingDir = path
        self.speedInKmh = float( speedAndFPS[0] )
        self.framesPerSec = float( speedAndFPS[1] )                
        self.xmlConfigName = "SceneDescription.xml"
        self.roadScene = modulRoadscene.RoadScene( self.workingDir, self.xmlConfigName )
        self.viewPoint = self.roadScene.targetParameters.viewPoint
        self.road = self.roadScene.scene.road
        self.target = self.roadScene.targetParameters.target

        self.calcNumberOfImages( )
        self.makeOct( )
        self.printRView( )
        self.makePic( )
        #self.postRenderProcessing( )
        self.deleteUnnecessaryFiles( )
        
        self.makeVideo( )

    def calcNumberOfImages( self ):
        print 'Generating images: drivin speed: ' + str( self.speedInKmh ) + ' km/h by ' + str( self.framesPerSec ) + 'frames per second'
        self.numberOfImages = int( ( ( self.roadScene.measFieldLength * self.framesPerSec * 3600  ) / ( 1000 * self.speedInKmh ) ) + 0.5 )
        print 'Numbers of generating video pictures: ' + str( self.numberOfImages )
    
    # system call to radiance framework to generate oct files out of the various rads
    def makeOct( self ):
        if( not os.path.isdir( self.workingDir + VideoSimulator.octDirSuffix ) ):
            os.mkdir( self.workingDir + VideoSimulator.octDirSuffix )

        for i in range( self.numberOfImages ):
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/night_sky.rad > {2}/sceneVideo{1}.oct'.format( self.workingDir + VideoSimulator.radDirSuffix, i, self.workingDir + VideoSimulator.octDirSuffix )
            os.system(cmd)
            print 'generated oct# ' + str( i )

    # system call to radiance framework to generate vp files
    def printRView( self ):

        viewDirection = "0 0.999847 -0.017467 "

        print 'Generating: videoView.vp'
        print '    viewpoint x-offset: ' + str( self.viewPoint.xOffset )
        print '    viewpoint view direction: ' + str( viewDirection )
        print '    viewpoint height: ' + str( self.viewPoint.height )

        for i in range( self.numberOfImages ):
            f = open( self.workingDir + VideoSimulator.radDirSuffix + '/videoView' + str( i ) + '.vp', "w" )
            f.write( "######videoView.vp######\n" )
            f.write( "rview -vtv -vp " + str( ( self.road.laneWidth * ( self.target.onLane + 0.5 ) ) + self.viewPoint.xOffset ) + " " + str( i * ( self.roadScene.measFieldLength / self.numberOfImages ) ) + " " + str( self.viewPoint.height ) + " -vd " + viewDirection + " -vh " + str( self.roadScene.verticalAngle ) + " -vv " + str( self.roadScene.horizontalAngle ) + "\n" )
            f.close( )

    #System call to radiance framework for the actual rendering of the images
    def makePic( self ):
        starttime = datetime.datetime.now()
        if( not os.path.isdir( self.workingDir + VideoSimulator.picDirSuffix ) ):
            os.mkdir( self.workingDir + VideoSimulator.picDirSuffix )
        if( not os.path.isdir( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix ) ):
            os.mkdir( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix )
        if( not os.path.isdir( self.workingDir + '/VideoTiffs/' ) ):
            os.mkdir( self.workingDir + '/VideoTiffs/' )

        for i in range( self.numberOfImages ):
            cmd0 = 'rpict -vtv -vf {3}/videoView{1}.vp -x {4} -y {5} {0}/sceneVideo{1}.oct > {2}/picsForVideo{1}.hdr'.format( self.workingDir + VideoSimulator.octDirSuffix , i, self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix, self.workingDir + VideoSimulator.radDirSuffix, VideoSimulator.horizontalRes, VideoSimulator.verticalRes )
            os.system( cmd0 )
            
            print 'maked hdr pic. Number: ' + str( i )
            
            if ( i < 10 ):
                cmdTiff = 'ra_tiff -e +8 {0}/picsForVideo{1}.hdr {2}/VideoTiffs/picsForVideo00{1}.tiff'.format( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix, i, self.workingDir )
                os.system( cmdTiff )
            elif ( i > 9 ) and ( i < 99 ):
                cmdTiff = 'ra_tiff -e +8 {0}/picsForVideo{1}.hdr {2}/VideoTiffs/picsForVideo0{1}.tiff'.format( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix, i, self.workingDir )
                os.system( cmdTiff )
            elif ( i > 100 ):
                cmdTiff = 'ra_tiff -e +8 {0}/picsForVideo{1}.hdr {2}/VideoTiffs/picsForVideo{1}.tiff'.format( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix, i, self.workingDir )
                os.system( cmdTiff )
                
            print 'maked tiff pic.'
            
            #cmdConvToJPG = 'tiffutil -lzw {2}/VideoTiffs/picsForVideo{1}.tiff -out {2}/VideoTiffs/picsForVideo{1}.jpg'.format( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix, i, self.workingDir )
            #os.system( cmdConvToJPG )
            
            #print 'maked jpg pic.'
            print datetime.datetime.now() - starttime
            
        print 'done.'
        print datetime.datetime.now() - starttime

    #Here the generated hdr images are converted to the pf format.
    #This involves using pvalue(radiance) to determine the luminance values of each pixel (-b option
    #gives radiance values, rcalc converts them to luminance values.
    #These values are dumped into a text file. the text file is then parsed and
    #are written into the final binary output pf file with the predefined header.
    def postRenderProcessing( self ):
        #create direction for temporarily save luminance txt files
        if( not os.path.isdir( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix + VideoSimulator.lumSubDirSuffix ) ):
                os.mkdir( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix + VideoSimulator.lumSubDirSuffix )

        #find all .hdr images named "out[i].hdr in pics directory
        processingList = []
        dirList = os.listdir( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix )
        for entry in dirList:
            if( not os.path.isdir( entry ) ):
                if( "picsForVideo" in entry ):
                    processingList.append( entry )

        #using pvalue (radiance) to determine the luminance values of each pixel (-b option
        #gives radiance values, rcalc converts them to luminance values) and save them into txt file.
        print "dumping pvalues:"
        for pic in processingList:
            print "File: " + pic
            cmd = "pvalue -h -H -b " + self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix + '/' +pic + " | rcalc -e '$1=179*$3' > " + self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix + VideoSimulator.lumSubDirSuffix + '/' + pic.replace( ".hdr", ".txt" )
            os.system(cmd)
            print "done."

        #find all txt files containing luminance values
        processedList = []
        dirList2 = os.listdir( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix + VideoSimulator.lumSubDirSuffix )
        for entry in dirList2:
            if( not os.path.isdir( entry ) ):
                if( "picsForVideo" in entry ):
                    processedList.append( entry )

        #write all luminance values into binary pf file and add predefined header
        print "converting to .pf format"
        for txtFile in processedList:
            print "File: " + txtFile.replace( ".txt", ".pf" )
            imgData = []
            lumFile = open( self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix + VideoSimulator.lumSubDirSuffix + '/' + txtFile, 'r' )
            rgbReader = csv.reader( lumFile, delimiter = ' ' )
            for row in rgbReader:
                pixelData = []
                for item in row:
                    if( len(item ) != 0 ):
                        pixelData.append( float( item ) )
                imgData.append( pixelData )
            lumFile.close()
            
            if( not os.path.isdir( self.workingDir + '/VideoPFs/' ) ):
                os.mkdir( self.workingDir + '/VideoPFs/' )

            pfOut = open( str( self.workingDir + '/VideoPFs/' + txtFile.replace( ".txt", ".pf" ) ), 'wb' )
            cmd = 'Typ=Pic98::TPlane<float>\r\nLines={1}\r\nColumns={0}\r\nFirstLine=1\r\nFirstColumn=1\r\n\0'.format( VideoSimulator.horizontalRes ,VideoSimulator.verticalRes )
            pfOut.write( cmd )

            for pixel in imgData:
                pfOut.write( struct.pack( 'f', pixel[0] ) )

            pfOut.close()
            print "done"
        return

    #clean up and delete txt files
    def deleteUnnecessaryFiles( self ):
        rbgPath = self.workingDir + VideoSimulator.picDirSuffix + VideoSimulator.picSubDirSuffix + VideoSimulator.lumSubDirSuffix
        if( os.path.exists( rbgPath ) ):
            shutil.rmtree( rbgPath )
        return
        
    #make video frome single pics in
    def makeVideo( self ):
        # standard RGB tiff file
        path = str( self.workingDir ) + '/VideoTiffs/'

        cmdVideo = 'ffmpeg -f image2 -i {0}/picsForVideo%03d.tiff -b 1000k -r {1} {0}/picsForVideo.mpg'.format( path, self.framesPerSec )
        os.system( cmdVideo )
       
          