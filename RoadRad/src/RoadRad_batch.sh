#!/bin/bash
# start this shell script with ./RoadRad_batch.sh from the src directory
# please add the folder names of your scenes in the following array (devided by space characters):
dirArray=(Treskowstr_R3_T004_RP800 Treskowstr_R3_T010_RP800 Treskowstr_R3_T030_RP800 Treskowstr_R3_T050_RP800 Treskowstr_R3_T070_RP800 Treskowstr_R3_T100_RP800 Treskowstr_R3_oH_T004_RP800 Treskowstr_R3_oH_T010_RP800 Treskowstr_R3_oH_T030_RP800 Treskowstr_R3_oH_T050_RP800 Treskowstr_R3_oH_T070_RP800 Treskowstr_R3_oH_T100_RP800 Treskowstr_R3_H_T004_RP800 Treskowstr_R3_H_T010_RP800 Treskowstr_R3_H_T030_RP800 Treskowstr_R3_H_T050_RP800 Treskowstr_R3_H_T070_RP800 Treskowstr_R3_H_T100_RP800)

# please add your LMK database directory:
dirOfDatabase="d:/cygwin/home/Robert/GitUmgebung/LMK/LMK_Data_evaluation/database/dataset/"

for((i = 0; i<${#dirArray[*]}; i++));
do 
	./RoadRad.py --dir ${dirArray[$i]};
	mkdir -p $dirOfDatabase/${dirArray[$i]}
	cd ..
	cp -R scenes/${dirArray[$i]} $dirOfDatabase/
	cd src/
done

