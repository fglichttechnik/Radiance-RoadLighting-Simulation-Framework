#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
# This Python file uses the following encoding: utf-8
import LIDC as modulLIDC
from lxml import etree

class LIDCs:
    def __init__( self, root ):
        self.lidcs = []      
        
        #load luminous intensity distribution curve
        self.loadLIDCs( root )
        
    def loadLIDCs( self, root ):
        lidcDesc = root.findall( 'LIDCs/LIDC' )
        for lidcEntry in lidcDesc:
            lidc = modulLIDC.LIDC( )
            lidc.name = lidcEntry.get( 'Name' )
            lidc.lightSource = lidcEntry.get( 'LightSource' )
            lidc.lightLossFactor = float( lidcEntry.get( 'LightLossFactor' ) )
            lidc.spRatio = float( lidcEntry.get( 'SPRatio' ) )
            self.lidcs.append( lidc )
            
        print '    lidcs loaded ...' 
