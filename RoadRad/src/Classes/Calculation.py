from lxml import etree

class Calculation:

    def __init__( self, root ):
        self.din13201= "" 
        self.veilingLuminance = "" 
        self.veilingLuminanceMethod = "" 
        self.tresholdLuminanceFactor = 0
        
        self.loadCalculation( root )
        
    def loadCalculation( self, root ): 
        calcDesc = root.find( 'Scene/Calculation' )
        self.din13201 = calcDesc.get( 'DIN13201' )
        self.veilingLuminance = calcDesc.get( 'VeilingLuminance' )
        self.veilingLuminanceMethod = calcDesc.get( 'VeilingLuminanceMethod' )
        self.tresholdLuminanceFactor = calcDesc.get( 'TresholdLuminanceFactor' )
        
        print '    calculation parameters loaded ...'