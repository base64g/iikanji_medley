#!/bin/sh
i=0
echo `od -A n -t u4 -N 4 /dev/urandom | sed 's/[^0-9]//g'`
musics=(`ls PartMusic`)
size=${#musics[*]}
toplay=${musics[`od -A n -t u4 -N 4 /dev/urandom | sed 's/[^0-9]//g'`%$size]}
sox "PartMusic/$toplay" output.wav norm
while [ $i -le 500 ];
do
    toplay=${musics[`od -A n -t u4 -N 4 /dev/urandom | sed 's/[^0-9]//g'`%$size]}
    echo $toplay
    echo "PartMusic/$toplay"
    sox PartMusic/${toplay} add.wav norm
    sox output.wav add.wav output2.wav
    mv output2.wav output.wav
    rm add.wav
    i=$((i + 1));
done
