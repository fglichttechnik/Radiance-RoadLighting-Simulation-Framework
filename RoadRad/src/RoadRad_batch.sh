#!/bin/bash
# start this shell script with ./RoadRad_batch.sh from the src directory
# please add the folder names of your scenes in the following array (devided by space characters):
dirArray=(CELEST_55W CIVIC_100W DECOSTREET_70W DYANA_150W INDRA_33W JET_42W LEMNIS_70W ORACLES_100W RIGA_70W VICTOR_40W)

# please add your LMK database directory:
dirOfDatabase="/Users/robert/Desktop/Development/LMK/LMK_Data_Evaluation/database/datasets/"

for((i = 0; i<${#dirArray[*]}; i++));
do 
	./RoadRad.py --dir ${dirArray[$i]};
	mkdir -p $dirOfDatabase/${dirArray[$i]}
	cd ..
	cp -R scenes/${dirArray[$i]} $dirOfDatabase/
	cd src/
done

