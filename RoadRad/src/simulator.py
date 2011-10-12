# This Python file uses the following encoding: utf-8

import os
import datetime
import Image


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
        
        if( self.makeRadfromIES( ) ):
            self.makeOct( )
            #self.makePic( )
            if( self.willMakeRefPic ):
                self.makeRefPic( )
                self.processRefPics( )

        return
    
    def makeRadfromIES( self ):
        if( not os.path.isdir( self.rootDirPath + self.ldcSuffix ) ):
            print "LDC not found in the designated LDCs directory"
            return False
        
        dirList = os.listdir( self.rootDirPath + self.ldcSuffix )
        for entry in dirList:
            if( entry.endswith( ".ies") ):
                self.iesPath = self.rootDirPath + self.ldcSuffix + '/' + entry
                cmd = 'ies2Rad -l ' + self.rootDirPath + self.ldcSuffix + ' ' + self.iesPath
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
                
            for i in range( 14 ):
                print 'generating pic# ' + str( i )
                starttime = datetime.datetime.now()
                #pfilt out, make raw image.1380x1030. vh and vv needs to calculated.
                cmd0 = 'rpict -vtv -vp 15 -273 4.75 -vd 0 0.999856 -0.0169975 -x 1000 -y 1000 -vh 25 -vv 25 {0}/scene{1}.oct | pfilt -r .6 -e 5 > {2}/out{1}.pic '.format( self.rootDirPath + self.octDirSuffix , i, self.rootDirPath + self.picDirSuffix )
                cmd1 = 'ra_tiff {0}/out{1}.pic {0}/out{1}.tiff'.format( self.rootDirPath + self.picDirSuffix, i )
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
        im = Image.open(self.rootDirPath + self.refPicDirSuffix + '/out0.tiff')
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
        return

