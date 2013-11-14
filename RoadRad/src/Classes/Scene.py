#AUTHOR: Jan Winter, Sandy Buschmann, Robert Franke TU Berlin, FG Lichttechnik,
#	j.winter@tu-berlin.de, www.li.tu-berlin.de
#LICENSE: free to use at your own risk. Kudos appreciated.
# This Python file uses the following encoding: utf-8
import Description as modulDescription
import Road as modulRoad
import Calculation as modulCalculation

class Scene:
    def __init__( self, root ):
        self.description = modulDescription.Description( root )
        self.road = modulRoad.Road( root )
        self.calculation = modulCalculation.Calculation( root )