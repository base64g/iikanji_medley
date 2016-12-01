#!/bin/sh
i=0
musics=(`ls PartMusic`)
size=${#musics[*]}
toplay=${musics[$RANDOM%$size]}
cp "PartMusic/$toplay" output.wav
while [ $i -le 100 ];
do
    toplay=${musics[$RANDOM%$size]}
    sox "PartMusic/$toplay" output.wav output.wav
    i=$((i + 1));
done
