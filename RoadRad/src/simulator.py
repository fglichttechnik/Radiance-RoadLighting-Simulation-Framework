# This Python file uses the following encoding: utf-8

import os

class simulator:
    
    def __init__(self, path):
        
        self.rootDirPath = path
        self.dirIndex = []
        
        dirList = os.listdir( self.rootDirPath )
        for entry in dirList:
            if( os.path.isdir( entry ) ):
                if( "scene" in entry ):
                    self.dirIndex.append( self.rootDirPath + '/' + entry )
        
        self.makeOct( )
        self.makePic( )
        return
    
    def makeOct(self):
        for entry in self.dirIndex:
            cmd = 'oconv {0}/materials.rad {0}/road.rad {0}/lights_s.rad {0}/target_0.rad {0}/night_sky.rad > {0}/scene.oct'.format( entry )
            #print cmd
            os.system(cmd)
        return
    
    def makePic(self):
        for entry in self.dirIndex:
            cmd = 'rpict -vtv -vp 28 -273 4.75 -vd 0 0.999856 -0.0169975 -vh 25 -vv 12.5 {0}/scene.oct > {0}/scene.pic'.format( entry )
            #print cmd
            os.system( cmd )
        return