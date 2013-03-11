import Target as modulTarget
import ViewPoint as modulViewPoint

class TargetParameters:
    def __init__( self, root ):
        self.viewPoint = modulViewPoint.ViewPoint( root )
        self.target = modulTarget.Target( root )