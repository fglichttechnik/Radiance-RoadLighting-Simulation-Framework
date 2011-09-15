#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import os

class EnvVarSetter:
    
    def __init__( self, path ):
        
        self.radiancePath = path
        
    def testRadianceInstall( self, path="" ):
        if( len( path) > 0 ):
            cmd = path + '/oconv'
        else:
            cmd = 'oconv'

        test = os.popen( cmd )
        for i in test.readlines( ):
            i.find( "RADIANCE" )
            print "Radiance installed properly."
            return True
        return False
    
    def addRadianceEnv( self ):
        if( not self.testRadianceInstall( self.radiancePath ) ):
            print"Radiance installation not found at provided path"
            return
        
        if( not os.path.isfile( "~/.profile" ) ):
            pathfile = open( "~/.profile", "w" )
        else:
            pathfile = open( "~/.profile", "a" )
        
        pathfile.write( "export PATH=$PATH:" + self.path +"/bin" )
        pathfile.close( )
        print "Please log out and back in, and run this script with the same option to test your installation"