#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
class Headlight:

    def __init__( self ):
        self.lidc = "" 
        self.headlightDistanceMode = "" 
        self.distance = 0 
        self.height = 0 
        self.width = 0 
        self.slopeAngle = 0 
        self.lightDirection = ""
        self.onLane = 0