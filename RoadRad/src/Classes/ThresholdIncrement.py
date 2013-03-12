# This Python file uses the following encoding: utf-8

import os
import math
import shutil
import sys
import csv
import struct
import Classes.RoadScene as modulRoadscene

class ThresholdIncrement:
	
	#fixed variables
	
	#constructor
	def __init__( self, roadRadObject ):
	
	self.roadScene = roadRadObject
	self.viewPoint = self.roadScene.targetParameters.viewPoint
    self.poles = self.roadScene.poles.poles
    
    self.makeOct( )
    self.calcVeilingLum( )
    self.calcTheta( )
    