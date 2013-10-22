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
        
        