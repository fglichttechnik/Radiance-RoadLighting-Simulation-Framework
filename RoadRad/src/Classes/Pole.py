#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
class Pole:

    def __init__( self, isSingle ):
        self.isSingle = isSingle
        if not self.isSingle:
            self.height = 0 
            self.spacing = 0 
            self.overhang = 0 
            self.isStaggered = "" 
            self.lidc = "" 
            self.side = ""
        if self.isSingle:
            self.height = 0 
            self.overhang = 0 
            self.lidc = "" 
            self.positionY = 0 
            self.side = ""