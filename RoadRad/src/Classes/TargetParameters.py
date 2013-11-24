#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
import Target as modulTarget
import ViewPoint as modulViewPoint

class TargetParameters:
    def __init__( self, root ):
        self.viewPoint = modulViewPoint.ViewPoint( root )
        self.target = modulTarget.Target( root )