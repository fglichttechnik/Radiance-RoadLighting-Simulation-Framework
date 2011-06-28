# This Python file uses the following encoding: utf-8

import csv
import os
import sys

#retrieve working directory info
currentDirName = os.path.dirname( sys.argv[ 0 ] ) + '/'

#open conf file for parsing
inputParser = csv.reader( open( currentDirName + 'roadRad.conf') )

mode = ''
sceneLengths = [ ]
pavementWidths = [ ]
sidewalkWidths = [ ]
grassWidths = [ ]
numLanes = [ ]
poleHeight = [ ]
isStaggered = [ ]
poleSpacing = [ ]

#parse conf file
for row in inputParser:
	if( len( row ) == 0 ):
		continue
		
	if( len( row ) == 1 ):
		if( len( row[0] ) > 5 ):
			mode = row[ 0 ][ 1: ]
		continue

	if( mode == 'StreetScene' ):
		sceneLengths.append( int( row[ 0 ][ row[ 0 ].lstrip( ).find( ' ' ) + 1: ] ) )
		pavementWidths.append( int( row[ 1 ][ row[ 1 ].lstrip( ).find( ' ' ) + 1: ] ) )
		sidewalkWidths.append( int( row[ 2 ][ row[ 2 ].lstrip( ).find( ' ' ) + 1: ] ) )
		grassWidths.append( int( row[ 3 ][ row[ 3 ].lstrip( ).find( ' ' ) + 1: ] ) )
		numLanes.append( int( row[ 4 ][ row[ 4 ].lstrip( ).find( ' ' ) + 1: ] ) )
		
	if( mode == 'PoleStats' ):
		poleHeight.append( int( row[ 0 ][ row [ 0 ].lstrip( ).find( ' ' ) + 1: ] ) )
		poleSpacing.append( int( row[ 1 ][ row [ 1 ].lstrip( ).find( ' ' ) + 1: ] ) )
		isStaggered.append( bool( row[ 2 ][ row [ 2 ].lstrip( ).find( ' ' ) + 1: ] ) )
		
print poleHeight
print poleSpacing
print isStaggered

for i in range( 0, len( sceneLengths ) ):
	os.mkdir( currentDirName + 'scene' + str( i ) )
	f = open( currentDirName + 'scene' + str( i ) + '/road.rad', 'w' )
	
	f.write( '######road.rad######\npavement polygon pave_surf\n0\n0\n12\n' )
	f.write( "%d -%d %d\n" % ( 0, sceneLengths[ i ] / 2, 0 ) )
	f.write( "%d -%d %d\n" % ( numLanes[ i ], sceneLengths[ i ] / 2, 0 ) )
	f.write( "%d %d %d\n" % ( numLanes[ i ], sceneLengths[ i ] / 2, 0 ) )
	f.write( "%d %d %d\n\n" % ( 0, sceneLengths[ i ] / 2, 0 ) )
	f.write( "!genbox concrete curb1 6 %d .5 | xform -e -t -6 -%d 0\n" % ( sceneLengths[ i ], sceneLengths[ i ] / 2 ) )
	f.write( "!genbox concrete curb2 6 %d .5 | xform -e -t %d -%d 0\n" % ( sceneLengths[ i ], numLanes[ i ], sceneLengths[ i ] / 2 ) )
	f.write( "!xform -e -t 23.6667 -%d .001 -a 2 -t .6667 0 0 solidyellow.rad\n" % ( sceneLengths[ i ] / 2 ) )
	f.write( "!xform -e -t 12 -%d .001 -a 120 -t 0 20 0 -a 2 -t 24 0 0 dashed_white.rad\n\n" % ( sceneLengths[ i ] ) )
	
	f.write( 'grass polygon lawn1\n0\n0\n12\n' )
	f.write( "-%d -%d .5\n" % ( 6, sceneLengths[ i ] / 2 ) )
	f.write( "-%d %d .5\n" % ( 6, sceneLengths[ i ] / 2 ) )
	f.write( "-%d %d .5\n" % ( 506, sceneLengths[ i ] / 2 ) )
	f.write( "-%d -%d .5\n\n\n" % ( 506, sceneLengths[ i ] / 2 ) )
	
	f.write( 'grass polygon lawn2\n0\n0\n12\n' )
	f.write( "%d -%d .5\n" % ( 54, sceneLengths[ i ] / 2 ) )
	f.write( "%d %d .5\n" % ( 54, sceneLengths[ i ] / 2 ) )
	f.write( "%d %d .5\n" % ( 554, sceneLengths[ i ] / 2 ) )
	f.write( "%d -%d .5\n" % ( 554, sceneLengths[ i ] / 2 ) )