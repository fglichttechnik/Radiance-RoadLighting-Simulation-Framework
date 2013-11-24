# This Python file uses the following encoding: utf-8
import Description as modulDescription
import Road as modulRoad
import Calculation as modulCalculation

class Scene:
    def __init__( self, root ):
        self.description = modulDescription.Description( root )
        self.road = modulRoad.Road( root )
        self.calculation = modulCalculation.Calculation( root )