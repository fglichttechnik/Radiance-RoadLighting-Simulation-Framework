# This Python file uses the following encoding: utf-8
import Description as modulDescription
import Road as modulRoad
import Calculation as modulCalculation

class Scene:
    def __init__( self ):
        self.description = modulDescription.Description()
        self.road = modulRoad.Road()
        self.calculation = modulCalculation.Calculation()