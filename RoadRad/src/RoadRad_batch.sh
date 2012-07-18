#!/bin/bash
# start this shell script with ./RoadRad_batch.sh from the src directory

# please add the folder names of your scenes in the following array (devided by space characters):
dirArray=(Sebastian_Juri_Simulation)

# please add your LMK database directory:		
dirOfDatabase="/Users/sandy/Desktop/Development/LMK/LMK_Data_evaluation/database"

for((i = 0; i<${#dirArray[*]}; i++));
do 
	./RoadRad.py --dir ${dirArray[$i]};
	mkdir -p $dirOfDatabase/${dirArray[$i]}
	cd ..
	cp -R scenes/${dirArray[$i]} $dirOfDatabase/
	cd src/
done
			


