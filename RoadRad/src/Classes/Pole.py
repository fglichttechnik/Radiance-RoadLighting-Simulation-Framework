class Pole:

    def __init__( self, isSingle ):
        self.isSingle = isSingle
        if not self.isSingle:
            self.height = 0 
            self.spacing = 0 
            self.overhang = 0 
            self.isStaggered = True 
            self.lidc = "" 
            self.side = ""
        if self.isSingle:
            self.height = 0 
            self.overhang = 0 
            self.lidc = "" 
            self.positionX = 0 
            self.side = ""