# This Python file uses the following encoding: utf-8

import os
import datetime

class simulator:
    
    def __init__(self, path):
        
        self.rootDirPath = path
        self.dirIndex = []
        
        dirList = os.listdir( self.rootDirPath + "/scenes/" )
        print dirList
        for entry in dirList:
            print entry
            print os.path.isdir( entry )
            #if( os.path.isdir( entry ) ):
            #    print "Found dir."
            if( "scene" in entry ):
                print "Found: " + entry
                self.dirIndex.append( self.rootDirPath + '/scenes/' + entry )
        
        print self.dirIndex
        
        self.makeOct( )
        self.makePic( )
        return
    
    def makeOct(self):
        for entry in self.dirIndex:
            for i in range( 14 ):
                cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/target_{1}.rad {0}/night_sky.rad > {0}/scene{1}.oct'.format( entry, i )
                os.system(cmd)
                print 'generated oct# ' + str( i )
        return
    
    def makePic(self):
        for entry in self.dirIndex:
            for i in range( 14 ):
                print 'generating pic# ' + str( i )
                starttime = datetime.datetime.now()
                cmd0 = 'rpict -vtv -vp 18 -273 4.75 -vd 0 0.999856 -0.0169975 -x 1000 -y 500 -vh 25 -vv 12.5 {0}/scene{1}.oct | pfilt -r .6 -e 5 > {0}/out_hr{1}.pic'.format( entry, i )
                os.system( cmd0 )
                print 'done.'
                print datetime.datetime.now() - starttime
            
                #cmd1 = 'rpict -vtv -vp 18 -273 4.75 -vd 0 0.999856 -0.0169975 -vu 0 0 1 -vh 6 -vv 3 -vs 0 -vl 0 -x 3000 -y 1500 {0}/scene.oct | pfilt -r .6 -x 800 -y 400 -1 -e 5 > {0}/scene1.pic'.format( entry )
                #os.system( cmd1 )
            
                #cmd2 = 'rpict -x 500 -y 2000 -vtl -vp 18 -150 4 -vd 0 0 -1 -vu 0 1 0 -vh 100 -vv 400 -vs 0 -vl 0 {0}/scene.oct | pfilt -x 200 -y 800 -r .6 -1 -e 200 > {0}/scene2.pic'.format( entry )
                #print cmd
                #os.system( cmd2 )
        return