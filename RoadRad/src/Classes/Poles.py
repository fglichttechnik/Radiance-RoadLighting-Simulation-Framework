# This Python file uses the following encoding: utf-8
import Pole as modulPole
from lxml import etree

class Poles:
    def __init__( self, root ):
        self.poles = []    
        
        #load pole array or single pole
        self.loadPoles( root )
        
    def loadPoles( self, root ):
        poleDesc = root.find( 'Poles' )

        for poleEntry in poleDesc:
            if( poleEntry.tag == 'PoleSingle' ):
                pole = modulPole.Pole( True )
                pole.positionY = float( poleEntry.get( 'PositionY' ) )

            else:
                pole = modulPole.Pole( False )
                pole.spacing = float( poleEntry.get( 'Spacing' ) )
                isStaggered = poleEntry.get( 'IsStaggered' )
                if isStaggered == 'False':
                    pole.IsStaggered = False
            
            pole.side = poleEntry.get( 'Side' )
            pole.height = float( poleEntry.get( 'Height' ) )
            pole.lidc = poleEntry.get( 'LIDC' )
            pole.overhang = float( poleEntry.get( 'Overhang' ) )
            self.poles.append( pole )
        
        print '    poles loaded ...' 