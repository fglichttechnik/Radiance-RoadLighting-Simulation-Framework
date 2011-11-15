# This Python file uses the following encoding: utf-8

import os
import datetime
import Image
from xml.dom.minidom import parse
import math
import csv
import struct

class simulator:
    
    def __init__( self, path, RefPic ):
        
        self.rootDirPath = path
        self.willMakeRefPic = RefPic
        self.octDirSuffix = '/Octs'
        self.refOctDirSuffix = '/RefOcts'
        self.radDirSuffix = '/Rads'
        self.refPicDirSuffix = '/RefPics'
        self.picDirSuffix = '/Pics'
        self.ldcSuffix = '/LDCs'
        self.iesPath = ''
        self.LMKSetMat = '/LMKSetMat'
        self.LMKSetMatFilename = '/pos.xml'
        self.sensorHeight = 8.9
        self.sendorWidth = 6.64
        self.picSubDirSuffix = '/pics'
        self.tiffSubDirSuffix = '/tiffs'
        self.pfSubDirPrefix = '/pfs'
        self.rgbSubDirPrefix = '/RGBs'
        
        if( self.makeRadfromIES( ) ):
            self.makeOct( )
            self.makePic( )
            if( self.willMakeRefPic ):
                self.makeRefPic( )
                self.processRefPics( )
        self.postRenderProcessing( )

        return
    
    def calcOpeningAngle( self, focalLength ):
        angles = []
        
        print 'Extracting focalLength.'
        configfile = open( self.workingDirPath + self.sceneDecriptor, 'r' )
        dom = parse( configfile )
        configfile.close( )
        
        focalLen = dom.getElementsByTagName( 'FocalLength' )
        if( focalLen.attributes ):
            fl = float( focalLen.attributes["fl"].value )
            
        angles[ 0 ] = 2 * math.atan( self.sensorHeight / ( 2 * fl ) )
        angles[ 1 ] = 2 * math.atan( self.sensorWidth / ( 2 * fl ) )
        
        return angles
    
    def makeRadfromIES( self ):
        if( not os.path.isdir( self.rootDirPath + self.ldcSuffix ) ):
            print "LDC not found in the designated LDCs directory"
            return False
        
        dirList = os.listdir( self.rootDirPath + self.ldcSuffix )
        for entry in dirList:
            if( entry.endswith( ".ies") ):
                self.iesPath = self.rootDirPath + self.ldcSuffix + '/' + entry
                cmd = 'ies2rad -l ' + self.rootDirPath + self.ldcSuffix + ' ' + self.iesPath
                os.system( cmd )
                break
        
        return True
    
    def makeOct(self):
        if( not os.path.isdir( self.rootDirPath + self.octDirSuffix ) ):
            os.mkdir( self.rootDirPath + self.octDirSuffix )
        
        for i in range( 14 ):
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/target_{1}.rad {0}/night_sky.rad > {2}/scene{1}.oct'.format( self.rootDirPath + self.radDirSuffix, i, self.rootDirPath + self.octDirSuffix )
            os.system(cmd)
            print 'generated oct# ' + str( i )
        
        if( self.makeRefPic ):
            if( not os.path.isdir( self.rootDirPath + self.refOctDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.refOctDirSuffix )
            
            for i in range( 14 ):
                cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/self_target_{1}.rad {0}/night_sky.rad > {2}/scene{1}.oct'.format( self.rootDirPath + self.radDirSuffix, i, self.rootDirPath + self.refOctDirSuffix )
                os.system(cmd)
                print 'generated refernce oct# ' + str( i )
    
    def makePic(self):
            if( not os.path.isdir( self.rootDirPath + self.picDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix )
            if( not os.path.isdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix )
            if( not os.path.isdir( self.rootDirPath + self.picDirSuffix + self.tiffSubDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix + self.tiffSubDirSuffix )
                
            for i in range( 14 ):
                print 'generating pic# ' + str( i )
                starttime = datetime.datetime.now()
                #pfilt out, make raw image.1380x1030. vh and vv needs to calculated.
                cmd0 = 'rpict -vtv -vp 15 -273 4.75 -vd 0 0.999856 -0.0169975 -x 1000 -y 1000 -vh 25 -vv 25 {0}/scene{1}.oct > {2}/out{1}.pic '.format( self.rootDirPath + self.octDirSuffix , i, self.rootDirPath + self.picDirSuffix +self.picSubDirSuffix )
                cmd1 = 'ra_tiff {0}/out{2}.pic {1}/out{2}.tiff'.format( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix, self.rootDirPath + self.picDirSuffix + self.tiffSubDirSuffix, i )
                os.system( cmd0 )
                os.system( cmd1 )
                print 'done.'
                print datetime.datetime.now() - starttime
            
                #cmd1 = 'rpict -vtv -vp 18 -273 4.75 -vd 0 0.999856 -0.0169975 -vu 0 0 1 -vh 6 -vv 3 -vs 0 -vl 0 -x 3000 -y 1500 {0}/scene.oct | pfilt -r .6 -x 800 -y 400 -1 -e 5 > {0}/scene1.pic'.format( entry )
                #os.system( cmd1 )
            
                #cmd2 = 'rpict -x 500 -y 2000 -vtl -vp 18 -150 4 -vd 0 0 -1 -vu 0 1 0 -vh 100 -vv 400 -vs 0 -vl 0 {0}/scene.oct | pfilt -x 200 -y 800 -r .6 -1 -e 200 > {0}/scene2.pic'.format( entry )
                #print cmd
                #os.system( cmd2 )
    
    def makeRefPic(self):
        if( not os.path.isdir( self.rootDirPath + self.refPicDirSuffix ) ):
                os.mkdir( self.rootDirPath + self.refPicDirSuffix )
        
        for i in range( 14 ):
                print 'generating Reference pic# ' + str( i )
                starttime = datetime.datetime.now()
                #pfilt out, make raw image.
                # -vf filename to integrate the eye file
                cmd0 = 'rpict -vtv -vp 15 -273 4.75 -vd 0 0.999856 -0.0169975 -x 1000 -y 500 -vh 25 -vv 12.5 {0}/scene{1}.oct | pfilt -r .6 -e 5 > {2}/out{1}.pic'.format( self.rootDirPath + self.refOctDirSuffix , i, self.rootDirPath + self.refPicDirSuffix )
                cmd1 = 'ra_tiff {0}/out{1}.pic {0}/out{1}.tiff'.format( self.rootDirPath + self.refPicDirSuffix, i )
                os.system( cmd0 )
                os.system( cmd1 )
                print 'done.'
                print datetime.datetime.now() - starttime
            
                #cmd1 = 'rpict -vtv -vp 18 -273 4.75 -vd 0 0.999856 -0.0169975 -vu 0 0 1 -vh 6 -vv 3 -vs 0 -vl 0 -x 3000 -y 1500 {0}/scene.oct | pfilt -r .6 -x 800 -y 400 -1 -e 5 > {0}/scene1.pic'.format( entry )
                #os.system( cmd1 )
            
                #cmd2 = 'rpict -x 500 -y 2000 -vtl -vp 18 -150 4 -vd 0 0 -1 -vu 0 1 0 -vh 100 -vv 400 -vs 0 -vl 0 {0}/scene.oct | pfilt -x 200 -y 800 -r .6 -1 -e 200 > {0}/scene2.pic'.format( entry )
                #print cmd
                #os.system( cmd2 )
                
    def processRefPics( self ):
        print "Processing reference pics."
        if( not os.path.isdir( self.rootDirPath + self.LMKSetMat ) ):
            os.mkdir( self.rootDirPath + self.LMKSetMat )
        
        xmlOut = open( self.rootDirPath + self.LMKSetMat + self.LMKSetMatFilename, 'w' )
        xmlOut.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<!DOCTYPE LMKSetMat SYSTEM \"LMKSetMat.dtd\">\n\n<LMKSetMat>\n" )
        
        for i in range( 14 ):
            im = Image.open(self.rootDirPath + self.refPicDirSuffix + '/out' + str(i) + '.tiff')
            pix = im.load()
            
            width, height = im.size
            
            xmin = 0
            xmax = 0
            ymin = 0
            ymax = 0
            
            for x in range(width):
                for y in range(height):
                    if( pix[ x, y ][ 0 ] == 255 and pix[ x, y ][ 1 ] == 255 and pix[ x, y ][ 2 ] == 255 ):
                        if( xmin == 0 and ymin == 0 ):
                            xmin = x
                            ymin = y
                        else:
                            xmax = x
                            ymax = y
            print xmin
            print ymin
            print xmax
            print ymax
            xmlOut.write( "<LMKData>\n<dataSource src=\"out"+str(i)+".mat\" type=\"mat\"/>\n<RectObject>\n<upperLeft x=\""+str(xmax)+"\" y=\""+str(ymax)+"\"/>\n<lowerRight x=\""+str(xmin)+"\" y=\""+str(ymin)+"\"/>\n<border pixel=\"0\"/>\n<position p=\"--\"/>\n</RectObject>\n</LMKData>\n\n" )
        xmlOut.close()          
        return
    
    def postRenderProcessing( self ):
        if( not os.path.isdir( self.rootDirPath + self.picDirSuffix + self.pfSubDirPrefix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix + self.pfSubDirPrefix )
        if( not os.path.isdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix +self.rgbSubDirPrefix ) ):
                os.mkdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix + self.rgbSubDirPrefix )
        
        processingList = []
        dirList = os.listdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix )
        for entry in dirList:
            if( not os.path.isdir( entry ) ):
                if( "out" in entry ):
                    processingList.append( entry )
        
        print "dumping pvalues:"
        for pic in processingList:
            print "File: " + pic
            cmd = "pvalue -h -H " + self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix + '/' +pic + "> " + self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix + self.rgbSubDirPrefix + '/' + pic.replace( ".pic", ".txt" )
            os.system(cmd)
            print "done."
        
        processedList = []
        dirList2 = os.listdir( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix + self.rgbSubDirPrefix )
        for entry in dirList2:
            if( not os.path.isdir( entry ) ):
                if( "out" in entry ):
                    processedList.append( entry )
        print "converting to .pf format"
        for txtFile in processedList:
            print "File: " +txtFile
            imgData = []
            rgbFile = open( self.rootDirPath + self.picDirSuffix + self.picSubDirSuffix + self.rgbSubDirPrefix + '/' + txtFile, 'r')
            rgbReader = csv.reader( rgbFile, delimiter = ' ' )
            for row in rgbReader:
                pixelData = []
                for item in row:
                    if( len(item ) != 0 ):
                        pixelData.append( float( item ) )
                imgData.append( pixelData )
            rgbFile.close()
            
            pfOut = open( str( self.rootDirPath + self.picDirSuffix + self.pfSubDirPrefix + '/' + txtFile.replace( ".txt", ".pf" ) ), 'wb' )
            pfOut.write('Typ=Pic98::TPlane<float>\r\nLines=1000\r\nColumns=1000\r\nFirstLine=1\r\nFirstColumn=1\r\n\0')
            
            #L = 179.R = 47.4.Rr + 119.9.Rg + 11.7.Rb
            for pixel in imgData:
                pfOut.write( struct.pack( 'f', 47.4 * pixel[2] + 119.9 * pixel[3] + 11.7 * pixel [4] ) )
            
            pfOut.close()
            print "done"
        return

