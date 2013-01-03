#!/bin/bash
# start this shell script with ./RoadRad_batch.sh from the src directory

#./RoadRad.py --dir Tr4
# ./RoadRad.py --dir Treskowstr_LED_RP8_4_undim
# ./RoadRad.py --dir Treskowstr_LED_RP8_4_ds
# ./RoadRad.py --dir Treskowstr_LED_RP8_4_dim
# ./RoadRad.py --dir Treskowstr_LED_RP8_undim
# ./RoadRad.py --dir Treskowstr_LED_RP8_ds
# ./RoadRad.py --dir Treskowstr_LED_RP8_dim
# ./RoadRad.py --dir Treskowstr_HS_RP8_1035
# ./RoadRad.py --dir Treskowstr_HS_RP8_1449
# ./RoadRad.py --dir Treskowstr_HS_RP8_2070
# ./RoadRad.py --dir Treskowstr_LED_RP8_1035
# ./RoadRad.py --dir Treskowstr_LED_RP8_1449
# ./RoadRad.py --dir Treskowstr_LED_RP8_2070
#./RoadRad.py --dir Schade_Optimierung_E
#./RoadRad.py --dir Schade_Optimierung_L

# please add the folder names of your scenes in the following array (devided by space characters):
dirArray=(Tr4)

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
			
