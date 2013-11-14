#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
class ThresholdIncrementData:

    def __init__( self, ev, theta, type, positionY, headlightType, position ):
        self.illuminance = float( ev ) 
        self.theta = float( theta )
        self.type = type # headlight or light
        self.positionY = float( positionY ) # distance or static value?
        self.veilingLum = 0.0
        
        if( self.type == "headlight" ):
            self.headlightType = headlightType # fixed or withTarget
            self.position = position # left or right
        
        