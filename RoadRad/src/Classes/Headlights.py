#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
# This Python file uses the following encoding: utf-8
import Headlight as modulHeadlight
from lxml import etree

class Headlights:
    def __init__( self, root ):
        self.headlights = []
        
        #load headlights
        self.loadHeadlights( root )
        
    def loadHeadlights( self, root ):
        headlightDesc = root.findall( 'Headlights/Headlight' )
        for headlightEntry in headlightDesc:
            headlight = modulHeadlight.Headlight( )
            headlight.lidc = headlightEntry.get( 'LIDC' ) 
            headlight.headlightDistanceMode = headlightEntry.get( 'HeadlightDistanceMode' ) 
            headlight.distance = float( headlightEntry.get( 'Distance' ) )
            headlight.height = float( headlightEntry.get( 'Height' ) )
            headlight.width = float( headlightEntry.get( 'Width' ) )  
            headlight.slopeAngle = float( headlightEntry.get( 'SlopeAngle' ) )
            headlight.lightDirection = headlightEntry.get( 'LightDirection' ) 
            headlight.onLane = int( headlightEntry.get( 'OnLane' )  ) - 1
            self.headlights.append( headlight )
         
        print '    headlights loaded ...'    
        