#!/bin/bash
# start this shell script with ./RoadRad_batch.sh from the src directory

# please add the folder names of your scenes in the following array (devided by space characters):
dirArray=(Treskowstr_LED_RP8_4 Treskowstr_LED_RP8_6 Treskowstr_LED_RP8_10 Treskowstr_LED_RP8_20 Treskowstr_LED_RP8_30 Treskowstr_LED_RP8_40 Treskowstr_LED_RP8_50 Treskowstr_LED_RP8_60 Treskowstr_LED_RP8_70 Treskowstr_LED_RP8_80 Treskowstr_LED_RP8_90 Treskowstr_LED_RP8_100)

# please add your LMK database directory:		
dirOfDatabase="/Users/sandy/Desktop/Development/LMK/"

for((i = 0; i<${#dirArray}; i++));
	do ./RoadRad.py --dir ${dirArray[$i]};
	echo ${dirArray[$i]};
done
			


