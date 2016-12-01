#!/bin/sh
i=0
musics=(`ls PartMusic`)
size=${#musics[*]}
toplay=${musics[$RANDOM%$size]}
cp "PartMusic/$toplay" output.wav
while [ $i -le 100 ];
do
    toplay=${musics[$RANDOM%$size]}
    echo $toplay
    echo "PartMusic/$toplay"
    sox output.wav PartMusic/${toplay} output2.wav
    mv output2.wav output.wav
    i=$((i + 1));
done
