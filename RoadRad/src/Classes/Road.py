#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
from lxml import etree

class Road:

    def __init__( self, root ):
        self.numLanes = 0
        self.numPoleFields = 0 
        self.laneWidth = 0 
        self.sidewalkWidth = 0 
        self.surface = "" 
        self.qZero = 0
        
        self.loadRoad( root ) 
        
    def loadRoad( self, root ):
        roadDesc = root.find( 'Scene/Road' )
        self.numLanes = int( roadDesc.get( 'NumLanes' ) )
        self.numPoleFields = float( roadDesc.get( 'NumPoleFields' ) )
        self.laneWidth = float( roadDesc.get( 'LaneWidth' ) )
        self.sidewalkWidth = float( roadDesc.get( 'SidewalkWidth' ) )
        self.surface = roadDesc.get( 'Surface' )
        self.qZero = float( roadDesc.get( 'qZero' ) )

        #print the q0 factor of pavement surface depend on r-table
        if self.surface == 'R1' and self.qZero != 0.00:
            self.qZero = self.qZero / 0.1
        elif self.surface == 'R2' and self.qZero != 0.00:
            self.qZero = self.qZero / 0.07
        elif self.surface == 'R3' and self.qZero != 0.00:
            self.qZero = self.qZero / 0.07
        elif self.surface == 'R4' and self.qZero != 0.00:
            self.qZero = self.qZero / 0.08
        elif self.surface == 'C1' and self.qZero != 0.00:
            self.qZero = self.qZero / 0.1
        elif self.surface == 'C2' and self.qZero != 0.00:
            self.qZero = self.qZero / 0.07
            
        print '    road parameters loaded ...'