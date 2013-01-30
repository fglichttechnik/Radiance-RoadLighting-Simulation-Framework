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
class Videosimulator:

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

    def __init__( self, path, numberOfImages ):

        self.workingDir = path
        self.numberOfImages = int( numberOfImages )
        self.xmlConfigName = "SceneDescription.xml"
        self.roadScene = modulRoadscene.RoadScene( self.workingDir, self.xmlConfigName )
        self.viewPoint = self.roadScene.targetParameters.viewPoint
        self.road = self.roadScene.scene.road
        self.target = self.roadScene.targetParameters.target

        self.makeOct( )
        self.printRView( )
        self.makePic( )
        self.postRenderProcessing( )
        self.deleteUnnecessaryFiles( )

    # system call to radiance framework to generate oct files out of the various rads
    # both for the actual simulated image and the refernce pictures to determine the
    # pixel position of the target objects
    def makeOct( self ):
        if( not os.path.isdir( self.workingDir + Videosimulator.octDirSuffix ) ):
            os.mkdir( self.workingDir + Videosimulator.octDirSuffix )

        for i in range( self.numberOfImages ):
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/night_sky.rad > {2}/sceneVideo{1}.oct'.format( self.workingDir + Videosimulator.radDirSuffix, i, self.workingDir + Videosimulator.octDirSuffix )
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
            f = open( self.workingDir + Videosimulator.radDirSuffix + '/videoView' + str( i ) + '.vp', "w" )
            f.write( "######videoView.vp######\n" )
            f.write( "rview -vtv -vp " + str( ( self.road.laneWidth * ( self.target.onLane + 0.5 ) ) + self.viewPoint.xOffset ) + " " + str( i * ( self.roadScene.measFieldLength / self.numberOfImages ) ) + " " + str( self.viewPoint.height ) + " -vd " + viewDirection + " -vh " + str( self.roadScene.verticalAngle ) + " -vv " + str( self.roadScene.horizontalAngle ) + "\n" )
            f.close( )

    #System call to radiance framework for the actual rendering of the images
    def makePic( self ):
        starttime = datetime.datetime.now()
        if( not os.path.isdir( self.workingDir + Videosimulator.picDirSuffix ) ):
            os.mkdir( self.workingDir + Videosimulator.picDirSuffix )
        if( not os.path.isdir( self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix ) ):
            os.mkdir( self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix )

        for i in range( self.numberOfImages ):
            cmd0 = 'rpict -vtv -vf {3}/videoView{1}.vp -x {4} -y {5} {0}/sceneVideo{1}.oct > {2}/picsForVideo{1}.hdr '.format( self.workingDir + Videosimulator.octDirSuffix , i, self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix, self.workingDir + Videosimulator.radDirSuffix, Videosimulator.horizontalRes, Videosimulator.verticalRes )

            os.system( cmd0 )
            print datetime.datetime.now() - starttime
            print 'next pic.'

        print 'done.'
        print datetime.datetime.now() - starttime

    #Here the generated hdr images are converted to the pf format.
    #This involves using pvalue(radiance) to determine the luminance values of each pixel (-b option
    #gives radiance values, rcalc converts them to luminance values.
    #These values are dumped into a text file. the text file is then parsed and
    #are written into the final binary output pf file with the predefined header.
    def postRenderProcessing( self ):
        #create direction for temporarily save luminance txt files
        if( not os.path.isdir( self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix + Videosimulator.lumSubDirSuffix ) ):
                os.mkdir( self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix + Videosimulator.lumSubDirSuffix )

        #find all .hdr images named "out[i].hdr in pics directory
        processingList = []
        dirList = os.listdir( self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix )
        for entry in dirList:
            if( not os.path.isdir( entry ) ):
                if( "picsForVideo" and "hdr" in entry ):
                    processingList.append( entry )

        #using pvalue (radiance) to determine the luminance values of each pixel (-b option
        #gives radiance values, rcalc converts them to luminance values) and save them into txt file.
        print "dumping pvalues:"
        for pic in processingList:
            print "File: " + pic
            cmd = "pvalue -h -H -b " + self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix + '/' +pic + " | rcalc -e '$1=179*$3' > " + self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix + Videosimulator.lumSubDirSuffix + '/' + pic.replace( ".hdr", ".txt" )
            os.system(cmd)
            print "done."

        #find all txt files containing luminance values
        processedList = []
        dirList2 = os.listdir( self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix + Videosimulator.lumSubDirSuffix )
        for entry in dirList2:
            if( not os.path.isdir( entry ) ):
                if( "picsForVideo" in entry ):
                    processedList.append( entry )

        #write all luminance values into binary pf file and add predefined header
        print "converting to .pf format"
        for txtFile in processedList:
            print "File: " + txtFile.replace( ".txt", ".pf" )
            imgData = []
            lumFile = open( self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix + Videosimulator.lumSubDirSuffix + '/' + txtFile, 'r' )
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
            cmd = 'Typ=Pic98::TPlane<float>\r\nLines={1}\r\nColumns={0}\r\nFirstLine=1\r\nFirstColumn=1\r\n\0'.format( Videosimulator.horizontalRes ,Videosimulator.verticalRes )
            pfOut.write( cmd )

            for pixel in imgData:
                pfOut.write( struct.pack( 'f', pixel[0] ) )

            pfOut.close()
            print "done"
        return

    #clean up and delete txt files
    def deleteUnnecessaryFiles( self ):
        rbgPath = self.workingDir + Videosimulator.picDirSuffix + Videosimulator.picSubDirSuffix + Videosimulator.lumSubDirSuffix
        if( os.path.exists( rbgPath ) ):
            shutil.rmtree( rbgPath )
        return