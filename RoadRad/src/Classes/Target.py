from lxml import etree

class Target:

    def __init__( self, root ):
        self.size = 0 
        self.reflectancy = 0 
        self.specularity = 0 
        self.roughness = 0 
        self.position = "" 
        self.onLane = 0
        
        self.loadTarget( root )
        
    def loadTarget( self, root ):
        targetDesc = root.find( 'TargetParameters/Target' )
        self.size = float( targetDesc.get( 'Size' ) )
        self.reflectency = float( targetDesc.get( 'Reflectancy' ) )
        self.roughness = float( targetDesc.get( 'Roughness' ) )
        self.specularity = float( targetDesc.get( 'Specularity' ) )
        self.position = targetDesc.get( 'Position' )
        self.onLane = int( targetDesc.get( 'OnLane' ) ) - 1
        
        print '    target parameters loaded ...'
