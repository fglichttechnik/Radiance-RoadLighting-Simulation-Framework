#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
from lxml import etree

class Description:

    def __init__( self, root ):
        self.title = "" 
        self.environment = "" 
        self.focalLength = 0
        
        self.loadDescription( root )
        
    def loadDescription( self, root ):
        sceneDesc = root.find( 'Scene/Description' )
        self.title = sceneDesc.get( 'Title' )
        self.environment = sceneDesc.get( 'Environment' )
        self.focalLength = float( sceneDesc.get( 'FocalLength' ) )
        
        print '    description parameters loaded ...'