class ThresholdIncrementData:

    def __init__( self, ev, theta, type, positionY, headlightType ):
        self.illuminance = float( ev ) 
        self.theta = float( theta )
        # headlight or light
        self.type = type
        self.positionY = float( positionY )
        if( self.type == "headlight" ):
            # fixed or withTarget
            self.headlightType = headlightType
        