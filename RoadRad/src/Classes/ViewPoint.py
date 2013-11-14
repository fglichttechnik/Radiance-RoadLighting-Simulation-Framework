#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
from lxml import etree

class ViewPoint:

    def __init__( self, root ):
        self.distance = 0 
        self.height = 0 
        self.targetDistanceMode = "" 
        self.xOffset = 0 
        self.viewDirection = ""
        
        self.loadViewPoint( root )
        
    def loadViewPoint( self, root ):
        viewpointDesc = root.find( 'TargetParameters/ViewPoint' )
        self.distance = float( viewpointDesc.get( 'Distance' ) )
        self.height = float( viewpointDesc.get( 'Height' ) )
        self.targetDistanceMode = viewpointDesc.get( 'TargetDistanceMode' )
        self.xOffset = float( viewpointDesc.get( 'XOffset' ) )
        self.viewDirection = viewpointDesc.get( 'ViewDirection' )
        
        print '    viewpoint parameters loaded ...'
        