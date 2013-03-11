from lxml import etree

class Description:

    def __init__( self, root ):
        self.title = "" 
        self.environment = "" 
        self.focalLength = 0
        
        self.loadDescription( root )
        
    def loadDescription( self, root ):
        sceneDesc = root.find( 'Scene/Description' )
        self.title = sceneDesc.get( 'Title' )
        self.environment = sceneDesc.get( 'Environment' )
        self.focalLength = float( sceneDesc.get( 'FocalLength' ) )
        
        print '    description parameters loaded ...'